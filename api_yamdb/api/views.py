from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import IntegrityError
from rest_framework.views import APIView
from .mixins import CreateListDeleteMixinSet
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import User, Title, Category, Genre, Review
from api.serializers import (TitleSerializer, GenreSerializer,
                             CategorySerializer)

from api_yamdb.settings import OUR_EMAIL
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TitleFilter
from django.db.models import Avg

from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAdminModeratorOwnerOrReadOnly)
from .serializers import (TokenSerializer, UserSerializer, SignUpSerializer)
from .serializers import (CommentSerializer, ReviewSerializer,
                          ReadOnlyTitleSerializer)

from rest_framework.pagination import LimitOffsetPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.select_related('category').prefetch_related(
        'genre').all(
    ).annotate(Avg("reviews__score")).order_by("name")
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadOnlyTitleSerializer
        return TitleSerializer


class GenreViewSet(CreateListDeleteMixinSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'


class CategoryViewSet(CreateListDeleteMixinSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'


class UsersViewSet(viewsets.ModelViewSet):
    """View-класс реализующий операции модели Users."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )
    http_method_names = ['get', 'post', 'delete', 'patch']

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):

        if request.method == 'GET':
            serializer = UserSerializer(request.user)

            return Response(serializer.data)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)

        return Response(serializer.data)


class GetApiToken(APIView):
    """Получение JWT-токена и кода подтверждения"""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):

        serializer = TokenSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'confirmation_code': 'Неверный код подтверждения!'},
                status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:

            return Response(
                {'username': 'Пользователь не найден!'},
                status=status.HTTP_404_NOT_FOUND)

        if data.get('confirmation_code') == user.confirmation_code:
            token = RefreshToken.for_user(user).access_token

            return Response({'token': str(token)},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApiSignup(APIView):
    """Регистрация и получение кода подтверждения на email."""

    def send_confirmation_code(self, user):
        send_mail(
            subject='Регистрация на Yamdb',
            message=(
                'Для завершения регистрации на Yamdb отправьте запрос '
                f'с именем пользователя {user.username} и '
                f'кодом подтверждения {user.confirmation_code} '
                'на url - /api/v1/auth/token/.'
            ),
            from_email=OUR_EMAIL,
            recipient_list=[user.email]
        )

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        try:
            user, _ = User.objects.get_or_create(
                username=username,
                email=email
            )
        except IntegrityError:
            return Response("Проблемы", status=status.HTTP_400_BAD_REQUEST)
        user.confirmation_code = default_token_generator
        user.save()
        self.send_confirmation_code(user)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.select_related('title', 'author').all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'),
                                 title=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_review().comments.select_related('review',
                                                         'author').all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
