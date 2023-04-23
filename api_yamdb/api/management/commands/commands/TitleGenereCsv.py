import pandas as pd

from django.core.management.base import BaseCommand

from reviews.models import Title, Genre


class Command(BaseCommand):
    def handle(self, *args, **options):
        genre_data = pd.read_csv(
            'C:/Dev/api_yamdb/api_yamdb/static/data/titles.csv')
        for i, row in genre_data.iterrows():
            title = Title.objects.get(pk=row['title_id'])
            genre = Genre.objects.get(pk=row['genre_id'])
            title.genre.add(genre)
        print('Данные записаны в БД')
