from django.core.management.base import BaseCommand
import pandas as pd
from reviews.models import Genre


class Command(BaseCommand):
    help = 'import booms'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        df = pd.read_csv('C:/Dev/api_yamdb/api_yamdb/static/data/genre.csv')
        for name, slug in zip(df.name, df.slug):
            models = Genre(name=name, slug=slug)
            models.save()
