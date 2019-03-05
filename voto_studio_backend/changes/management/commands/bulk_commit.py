from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from voto_studio_backend.changes.models import Change


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--bypass', action='store', dest='bypass', help='Bypass the confirmation step')
        parser.add_argument('--user', action='store', dest='user', help='Clear instances for only this user')

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

        if confirm:
            changes = Change.objects.filter(user=user, committed=False)
            [change.commit() for change in changes]
            self.stdout.write(f'Committed {changes.count()} instances.')
        else:
            self.stdout.write('Cancelled.')
