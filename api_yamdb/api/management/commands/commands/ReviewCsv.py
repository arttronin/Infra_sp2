from django.core.management.base import BaseCommand
import pandas as pd
from reviews.models import Review


class Command(BaseCommand):
    help = 'import booms'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        df = pd.read_csv('C:/Dev/api_yamdb/api_yamdb/static/data/review.csv')
        for title, text, author, score, pub_date in zip(
                df.title_id, df.text, df.author, df.score, df.pub_date):
            models = Review(title_id=title, text=text, author=author,
                            score=score, pub_date=pub_date)
            models.save()
