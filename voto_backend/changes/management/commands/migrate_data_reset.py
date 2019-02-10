from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from data.regex import migrate


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('full_reset', bypass=True)
        call_command('bulk_indexing', 'default', bypass=True)
