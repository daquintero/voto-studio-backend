from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied


def permission_denied_message(obj, instance=None):
    return {
        **obj,
        'permitted': False,
        'id': instance.id,
        'model_label': instance._meta.model._meta.label,
    }


def get_object_or_403(model_class, operation_tuple, **kwargs):
    instance = get_object_or_404(model_class, **kwargs)
    user, operation = operation_tuple
    if instance.is_permitted(user, operation):
        return instance
    else:
        raise PermissionDenied(permission_denied_message({
            'message': f'You do not have {operation} permission on this content.',
        }, instance=instance))
