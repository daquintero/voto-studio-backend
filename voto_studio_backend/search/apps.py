from django.apps import AppConfig
from django.conf import settings
from .indexing import create_document_classes


class SearchConfig(AppConfig):
    name = 'voto_studio_backend.search'
    document_classes = {}

    def ready(self):
        from . import signals
        self.document_classes[settings.STUDIO_DB] = create_document_classes(using=settings.STUDIO_DB)
        self.document_classes[settings.MAIN_SITE_DB] = create_document_classes(using=settings.MAIN_SITE_DB)
