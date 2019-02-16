from rest_framework import serializers
from . import models


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.Image
        fields = (
            'id',
            'title',
            'url',
        )

    def get_url(self, obj):
        return obj.image.url


class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Video
        fields = (
            'id',
            'title',
            'embed_url',
        )


class ResourceSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.Video
        fields = (
            'id',
            'title',
            'url',
        )

    def get_url(self, obj):
        return obj.file.url
