import time

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from data.regex import migrate


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--user', action='store', dest='user', help='Clear instances for only this user')

    def handle(self, *args, **options):
        call_command('full_reset', bypass=True, user=options.get('user'))
        time.sleep(10)
        call_command('bulk_indexing', 'default', bypass=True)
