# from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint
from django.core.validators import MaxValueValidator, MinValueValidator
# User = get_user_model()


from django.contrib.auth.models import AbstractUser
from api.validators import validate_username


USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'


class User(AbstractUser):
    """Кастомная модель User."""

    ROLES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор')
    )
    username = models.CharField(
        verbose_name='Ник пользователя',
        validators=(validate_username,),
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        verbose_name='E-mail',
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=150,
        blank=True
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True
    )
    role = models.TextField(
        verbose_name='Роль пользователя',
        blank=True,
        choices=ROLES,
        default=USER
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        max_length=6,
        blank=True
    )

    class Meta:

        verbose_name = 'Пользователь',
        verbose_name_plural = 'Пользователи'

    def __str__(self):

        return str(self.username)

    @property
    def is_admin(self):

        return self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):

        return self.role == MODERATOR


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=150)
    slug = models.SlugField('Уникальный индификатор', unique=True,
                            max_length=50)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField('Категория', max_length=150)
    slug = models.SlugField('Уникальный индификатор', unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    year = models.IntegerField("Год выпуска")
    name = models.TextField('Название', max_length=72)
    description = models.TextField('Описание', max_length=200, null=True,
                                   blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 blank=True, null=True,
                                 related_name='Категория')
    genre = models.ManyToManyField(Genre, related_name='Жанр')
    rating = models.IntegerField('Рейтинг', null=True, default=None)

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель Отзывов"""
    text = models.TextField()
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, 'Допустимы значения от 1 до 10'),
            MaxValueValidator(10, 'Допустимы значения от 1 до 10')
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews',)

    class Meta:
        ordering = ('-pub_date',)
        constraints = [
            UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review')
        ]

    def __str__(self):
        return self.text[:30]


class Comment(models.Model):
    """Модель Комментариев"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:30]
