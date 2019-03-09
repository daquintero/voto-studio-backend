from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--spatial', action='store', dest='spatial', help='Migrate the spatial schema as well.')

    def handle(self, *args, **options):
        self.stdout.write(f"Migrating {settings.STUDIO_DB} database...")
        call_command('migrate', database=settings.STUDIO_DB)

        self.stdout.write(f"Migrating {settings.HISTORY_DB} database...")
        call_command('migrate', database=settings.HISTORY_DB)

        self.stdout.write(f"Migrating {settings.MAIN_SITE_DB} database...")
        call_command('migrate', database=settings.MAIN_SITE_DB)

        if options.get('spatial', False):
            self.stdout.write(f"Migrating {settings.SPATIAL_DB} database...")
            call_command('migrate', database=settings.SPATIAL_DB)

        self.stdout.write('Successfully migrated both databases.')
