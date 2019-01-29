from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save)
def create_or_update_document(sender, instance, created, using, **kwargs):
    if sender._meta.label not in settings.MODELS_TO_INDEX:
        return

    if created:
        obj = instance.create_document(using=using)
    else:
        obj = instance.update_document(using=using)


@receiver(post_delete)
def delete_document(sender, instance, using, **kwargs):
    if sender._meta.label not in settings.MODELS_TO_INDEX:
        return

    obj = instance.delete_document(using=using)
