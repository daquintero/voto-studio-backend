from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from ...utils import migrate_rels_dict
from shared.utils import get_model


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--using', action='store', dest='using', help='The DB to act on')

    def handle(self, *args, **options):
        using = options.get('using')
        if using is None:
            using = settings.STUDIO_DB

        self.stdout.write(f"Migrating {using} database...")
        call_command('migrate', database=using)

        for model_label in settings.WORKSHOP_MODELS:
            self.stdout.write(f'Rebuilding rels_dict for {model_label}')
            migrate_rels_dict(model_class=get_model(model_label=model_label), logging=True)

        self.stdout.write('Successfully migrated database and rels_dict.')
