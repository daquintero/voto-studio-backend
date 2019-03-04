from django.core.management import call_command
from django.core.management.base import BaseCommand
from data.regex import migrate


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--user', action='store', dest='user', help='Clear instances for only this user')

    def handle(self, *args, **options):
        user = options.get('user')

        ans = input(f'This will begin by clearing ALL change instances, ALl forms instances and reset ALL indices! '
                    f'Do you wish to continue? [y/N] ')
        confirm = ans.lower() == 'y'

        if confirm:
            self.stdout.write(f"Resetting data...")
            call_command('migrate_data_reset', user=user)
            self.stdout.write(f"Migrating data...")
            migrate(user=user)
            self.stdout.write('Successfully migrated data.')
        else:
            self.stdout.write('Cancelled.')
