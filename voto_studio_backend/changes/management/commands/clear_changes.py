from django.core.management.base import BaseCommand
from voto_studio_backend.changes.models import Change


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--bypass', action='store', dest='bypass', help='Bypass the confirmation step')

    def handle(self, *args, **options):
        if not options.get('bypass'):
            ans = input(f'This will clear ALL change instances! Do you wish to continue? [y/N] ')
            confirm = ans.lower() == 'y'
        else:
            confirm = True

        if confirm:
            change_count = Change.objects.count()
            Change.objects.all().delete()
            self.stdout.write(f'Deleted {change_count} change instances.')
        else:
            self.stdout.write('Cancelled.')
