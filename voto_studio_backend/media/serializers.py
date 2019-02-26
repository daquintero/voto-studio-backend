from rest_framework import serializers
from . import models


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    model_label = serializers.SerializerMethodField()

    class Meta:
        model = models.Image
        fields = (
            'id',
            'title',
            'url',
            'model_label',
        )

    def get_url(self, obj):
        return obj.image.url

    def get_model_label(self, obj):
        return obj._meta.model._meta.label


class VideoSerializer(serializers.ModelSerializer):
    model_label = serializers.SerializerMethodField()

    class Meta:
        model = models.Video
        fields = (
            'id',
            'title',
            'embed_url',
            'model_label',
        )

    def get_model_label(self, obj):
        return obj._meta.model._meta.label


class ResourceSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    model_label = serializers.SerializerMethodField()

    class Meta:
        model = models.Video
        fields = (
            'id',
            'title',
            'url',
            'model_label',
        )

    def get_url(self, obj):
        return obj.file.url

    def get_model_label(self, obj):
        return obj._meta.model._meta.label
