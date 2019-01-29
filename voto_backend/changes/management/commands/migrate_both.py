from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(f"Migrating {settings.MAIN_SITE_DB} database...")
        call_command('migrate', database=settings.MAIN_SITE_DB)

        self.stdout.write(f"Migrating {settings.STUDIO_DB} database...")
        call_command('migrate', database=settings.STUDIO_DB)

        self.stdout.write('Successfully migrated both databases.')
