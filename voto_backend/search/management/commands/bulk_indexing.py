from django.core.management.base import BaseCommand
from voto_backend.search.indexing import bulk_indexing


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('using', type=str)
        parser.add_argument('--bypass', action='store', dest='bypass', help='Bypass the confirmation step')

    def handle(self, *args, **options):
        using = options.get('using')

        if not options.get('bypass'):
            ans = input(f'This will bulk index all instances on the {using} alias! Do you wish to continue? [y/N] ')
            confirm = ans.lower() == 'y'
        else:
            confirm = True

        if confirm:
            self.stdout.write('Bulk indexing...')
            bulk_indexing(using=using)

            self.stdout.write('Successfully bulk indexed.')
        else:
            self.stdout.write('Cancelled.')
