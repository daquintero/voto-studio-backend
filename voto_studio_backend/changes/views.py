import copy

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from shared.utils import get_model


@api_view()
def increment_view_count(request):
    model_label = request.GET.get('ml')
    instance_id = request.GET.get('id')

    model_class = get_model(model_label=model_label)
    instance = get_object_or_404(model_class.objects.using(settings.MAIN_SITE_DB), id=instance_id)

    instance.views = instance.views + 1
    instance.save(using=settings.MAIN_SITE_DB)

    response = {
        'id': instance_id,
        'views': instance.views,
    }

    return Response(response, status=status.HTTP_200_OK)
