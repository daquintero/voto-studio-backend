from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from . import models
from . import serializers
from shared.utils import get_model


MODEL_SERIALIZER_MAP = {
    'media.Image': serializers.ImageSerializer,
    'media.Video': serializers.VideoSerializer,
    'media.Resource': serializers.ResourceSerializer,
}


class ListFileAPI(APIView):
    authentication_classes = (TokenAuthentication, )

    @staticmethod
    def get(request):
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        model_label = request.GET.get('ml')
        model_class = get_model(model_label=model_label)

        page_number = int(request.GET.get('page'))
        page_size = 24

        s1 = (page_number * page_size)
        s2 = (page_number * page_size) + page_size

        exclude_ids = request.GET.get('exclude').split('-')
        if not exclude_ids == ['']:
            instances = model_class.objects.exclude(id__in=exclude_ids).order_by('-date_uploaded')
        else:
            instances = model_class.objects.all().order_by('-date_uploaded')

        response = {
            'instances': MODEL_SERIALIZER_MAP[model_label](instances[s1:s2], many=True).data,
            'instance_count': model_class.objects.count(),
            'page_size': page_size,
            'page_number': page_number,
        }

        return Response(response, status=status.HTTP_200_OK)


class UploadFileAPI(APIView):
    authentication_classes = (TokenAuthentication, )

    @staticmethod
    def post(request):
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        model_label = request.data['model_label']
        model_class = get_model(model_label=model_label)

        instances = []
        for file in request.FILES.values():
            instance = model_class.objects.create(
                title=file.name,
                user=request.user,
            )
            model_class.save_file(file.name, file)
            instances.append(instance)

        response = {
            'instances': MODEL_SERIALIZER_MAP[model_label](instances, many=True).data,
            'image_count': model_class.objects.count(),
        }

        if response['instances']:
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class UpdateFileAPI(APIView):
    authentication_classes = (TokenAuthentication, )

    @staticmethod
    def post(request):
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        model_label = request.data.get('model_label')
        model_class = get_model(model_label=model_label)

        id = request.data.get('id')
        title = request.data.get('title')

        instance = get_object_or_404(model_class, id=id)
        instance.title = title
        instance.save(using=settings.STUDIO_DB)

        response = {
            'instance': MODEL_SERIALIZER_MAP[model_label](instance).data,
        }

        return Response(response, status=status.HTTP_200_OK)


class DeleteFilesAPI(APIView):
    authentication_classes = (TokenAuthentication, )

    @staticmethod
    def delete(request):
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        model_label = request.data.get('model_label')
        model_class = get_model(model_label=model_label)

        ids = [int(_id) for _id in request.data.get('ids')]
        instances = model_class.objects.filter(id__in=ids)
        for instance in instances:
            instance.delete(reduce_order=True)

        response = {
            'ids':  ids,
            'image_count': model_class.objects.count(),
        }

        return Response(response, status=status.HTTP_200_OK)
