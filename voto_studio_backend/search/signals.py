from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


def to_index(sender, instance, using=settings.STUDIO_DB):
    if sender._meta.label == settings.AUTH_USER_MODEL:
        return using == settings.STUDIO_DB
    return (sender._meta.label in settings.MODELS_TO_INDEX and
            instance.tracked and
            getattr(instance, 'to_index', True))


@receiver(post_save)
def create_or_update_document(sender, instance, created, using, **kwargs):
    if not to_index(sender, instance, using=using):
        return

    if created:
        obj = instance.create_document(using=using)
    else:
        obj = instance.update_document(using=using)


@receiver(post_delete)
def delete_document(sender, instance, using, **kwargs):
    if not to_index(sender, instance):
        return

    obj = instance.delete_document(using=using)
