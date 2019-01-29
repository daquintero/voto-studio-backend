from django.core.management.base import BaseCommand
from voto_backend.search import clear_indices


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('using', type=str)
        parser.add_argument('--bypass', action='store', dest='bypass', help='Bypass the confirmation step')

    def handle(self, *args, **options):
        using = options.get('using')

        if not options.get('bypass'):
            ans = input(f'This will clear ALL indices on the {using} alias! Do you wish to continue? [y/N] ')
            confirm = ans.lower() == 'y'
        else:
            confirm = True

        if confirm:
            self.stdout.write('Clearing indices...')
            clear_indices(using=using, confirm=confirm)

            self.stdout.write('Successfully cleared indices.')
        else:
            self.stdout.write('Cancelled.')
