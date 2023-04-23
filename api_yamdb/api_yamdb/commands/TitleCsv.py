from django.core.management.base import BaseCommand
import pandas as pd
from reviews.models import Title


class Command(BaseCommand):
    help = 'import booms'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        df = pd.read_csv('C:/Dev/api_yamdb/api_yamdb/static/data/titles.csv')
        for id, name, year, category in zip(df.id, df.name, df.year,
                                            df.category):
            models = Title(id=id, name=name, year=year, category=category)
            models.save()
