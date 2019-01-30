from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(f"Migrating {settings.STUDIO_DB} database...")
        call_command('migrate', database=settings.STUDIO_DB)

        self.stdout.write(f"Deleting 'django_migrations' table...")
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM django_migrations')

        self.stdout.write(f"Migrating {settings.MAIN_SITE_DB} database...")
        call_command('migrate', database=settings.MAIN_SITE_DB)

        self.stdout.write('Successfully migrated both databases.')
