from django.core.management.base import BaseCommand
import pandas as pd
from reviews.models import Comment


class Command(BaseCommand):
    help = 'import booms'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        df = pd.read_csv('C:/Dev/api_yamdb/api_yamdb/static/data/comments.csv')
        for review, text, author, pub_date in zip(df.review_id, df.text,
                                                  df.author, df.pub_date):
            models = Comment(review_id=review, text=text,
                             author=author, pub_date=pub_date)
            models.save()
