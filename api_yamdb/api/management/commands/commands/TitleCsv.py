from django.core.management.base import BaseCommand
import pandas as pd
from reviews.models import Title, Category


class Command(BaseCommand):
    help = 'import booms'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        tmp_data = pd.read_csv(
            'C:/Dev/api_yamdb/api_yamdb/static/data/titles.csv',
            sep=','
        )
        titles = [
            Title(id=row['id'], name=row['name'], year=row['year'],
                  category=Category.objects.get(pk=row['category']),)
            for i, row in tmp_data.iterrows()
        ]
        Title.objects.bulk_create(titles)
        print('Данные записаны в БД')
