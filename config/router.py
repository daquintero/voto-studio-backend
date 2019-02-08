from django.conf import settings


class GeneralRouter:
    """
    A router to control all database operations on models in the
    spatial application.
    """
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the settings.SPATIAL_DB
        database.
        """
        if app_label == 'spatial':
            return db == settings.SPATIAL_DB
        return True
