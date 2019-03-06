import math

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.http import Http404

from voto_studio_backend.changes.models import Change


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--bypass', action='store', dest='bypass', help='Bypass the confirmation step')
        parser.add_argument('--user', action='store', dest='user', help='Clear instances for only this user')
        parser.add_argument('--committed', action='store', dest='committed', help='Commit state of the instances')

    def handle(self, *args, **options):
        user = options.get('user')
        user = user if user is not None else 'migration@bot.com'
        filter_kwargs = {}
        if not user == 'all':
            user = get_user_model().objects.get(email=user)
            filter_kwargs.update({'user': user})

        if not options.get('bypass'):
            ans = input(f'This will commit ALL uncommitted change instances! Do you wish to continue? [y/N] ')
            confirm = ans.lower() == 'y'
        else:
            confirm = True

        committed = options.get('committed', False)
        if not committed == 'all':
            filter_kwargs.update({'committed': committed})

        if confirm:
            changes = Change.objects \
                .filter(**filter_kwargs) \
                .order_by('date_created')
            change_count = changes.count()
            for index, change in enumerate(changes):
                if not index % math.ceil(change_count / 10):
                    print(f'{round(index / change_count * 100)}%')
                try:
                    change.commit()
                except:
                    print('Skipped', change)
            self.stdout.write(f'Committed {changes.count()} instances.')
        else:
            self.stdout.write('Cancelled.')
