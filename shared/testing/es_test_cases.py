import time

from django.conf import settings
from django.test import TestCase
from voto_studio_backend.search.indexing import bulk_indexing, clear_indices


class ESTestCase(TestCase):
    def setUp(self):
        bulk_indexing(using=[settings.STUDIO_DB, settings.MAIN_SITE_DB])
        time.sleep(15)

    def tearDown(self):
        clear_indices(using=[settings.STUDIO_DB, settings.MAIN_SITE_DB])
