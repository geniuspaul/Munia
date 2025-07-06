from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Drops a specific table'

    def add_arguments(self, parser):
        parser.add_argument('table_name', type=str, help='Name of the table to drop')

    def handle(self, *args, **options):
        table = options['table_name']
        with connection.cursor() as cursor:
            cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
        self.stdout.write(self.style.SUCCESS(f'Table "{table}" dropped successfully.'))
