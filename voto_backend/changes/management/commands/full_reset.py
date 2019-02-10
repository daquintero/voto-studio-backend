from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--bypass', action='store', dest='bypass', help='Bypass the confirmation step')

    def handle(self, *args, **options):
        if not options.get('bypass'):
            ans = input(f'This will clear ALL change instances, ALl forms instances and reset ALL indices! '
                        f'Do you wish to continue? [y/N] ')
            confirm = ans.lower() == 'y'
        else:
            confirm = True

        if confirm:
            self.stdout.write(f"Clearing instances in '{settings.MAIN_SITE_DB}'...")
            call_command('clear_instances', settings.MAIN_SITE_DB, bypass=True)

            self.stdout.write(f"Clearing instances in '{settings.STUDIO_DB}'...")
            call_command('clear_instances', settings.STUDIO_DB, bypass=True)

            self.stdout.write("Clearing changes...")
            call_command('clear_changes', bypass=True)

            self.stdout.write(f"Clearing indices under alias '{settings.MAIN_SITE_DB}'...")
            call_command('clear_indices', 'main_site', bypass=True)

            self.stdout.write(f"Clearing indices under alias '{settings.STUDIO_DB}'...")
            call_command('clear_indices', 'default', bypass=True)

            self.stdout.write('---------------------------------------------')
            self.stdout.write('Full reset successful.')
        else:
            self.stdout.write('Cancelled.')
