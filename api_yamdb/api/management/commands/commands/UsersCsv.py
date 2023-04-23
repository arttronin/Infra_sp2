from django.core.management.base import BaseCommand
import pandas as pd
from users.models import User


class Command(BaseCommand):
    help = 'import booms'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        df = pd.read_csv('C:/Dev/api_yamdb/api_yamdb/static/data/users.csv')
        for username, email, role, bio, first_name, last_name in zip(
                df.username, df.email, df.role, df.bio, df.first_name,
                df.last_name):
            models = User(username=username, email=email, role=role,
                          bio=bio, first_name=first_name, last_name=last_name)
            models.save()
