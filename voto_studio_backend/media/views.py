from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from . import models
from . import serializers


class ListImageAPI(APIView):
    authentication_classes = (TokenAuthentication, )

    @staticmethod
    def get(request):
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        page_number = int(request.GET.get('page'))
        page_size = 24

        s1 = (page_number * page_size)
        s2 = (page_number * page_size) + page_size

        exclude_ids = request.GET.get('exclude').split('-')
        if not exclude_ids == ['']:
            images = models.Image.objects.exclude(id__in=exclude_ids).order_by('-date_uploaded')
        else:
            images = models.Image.objects.all().order_by('-date_uploaded')

        response = {
            'instances': serializers.ImageSerializer(images[s1:s2], many=True).data,
            'image_count': models.Image.objects.count(),
            'page_size': page_size,
            'page_number': page_number,
        }

        return Response(response, status=status.HTTP_200_OK)


class UploadImageAPI(APIView):
    authentication_classes = (TokenAuthentication, )

    @staticmethod
    def post(request):
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        image_instances = []
        for file in request.FILES.values():
            image_instance = models.Image.objects.create(
                title=file.name,
                user=request.user,
            )
            image_instance.image.save(file.name, file)
            image_instances.append(image_instance)

        response = {
            'instances': serializers.ImageSerializer(image_instances, many=True).data,
            'image_count': models.Image.objects.count(),
        }

        if response['instances']:
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class UpdateImageAPI(APIView):
    authentication_classes = (TokenAuthentication, )

    @staticmethod
    def post(request):
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        id = request.data.get('id')
        title = request.data.get('title')

        image_instance = get_object_or_404(models.Image, id=id)
        image_instance.title = title
        image_instance.save(using=settings.STUDIO_DB)

        response = {
            'instance': serializers.ImageSerializer(image_instance).data,
        }

        return Response(response, status=status.HTTP_200_OK)


class DeleteImageAPI(APIView):
    authentication_classes = (TokenAuthentication, )

    @staticmethod
    def delete(request):
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        ids = [int(_id) for _id in request.data.get('ids')]
        instances = models.Image.objects.filter(id__in=ids)
        for instance in instances:
            instance.delete(reduce_order=True)

        response = {
            'ids':  ids,
            'image_count': models.Image.objects.count(),
        }

        return Response(response, status=status.HTTP_200_OK)
