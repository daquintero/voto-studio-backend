from django.conf import settings


class SpatialRouter:
    """
    A router to control all database operations on models in the
    spatial application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to settings.SPATIAL_DB.
        """
        if model._meta.app_label == 'spatial':
            return settings.SPATIAL_DB
        return False

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to settings.SPATIAL_DB.
        """
        if model._meta.app_label == 'spatial':
            return settings.SPATIAL_DB
        return False

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the spatial app is involved.
        """
        if obj1._meta.app_label == 'spatial' or \
           obj2._meta.app_label == 'spatial':
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the spatial app only appears in the settings.SPATIAL_DB
        database.
        """
        if app_label == 'spatial':
            return db == settings.SPATIAL_DB
        return False
