from rest_framework import serializers
from content import models

# Serializers __________________________________________________________________________________________________


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ReadOnlyField(source='get_absolute_image_url')

    class Meta:
        model = models.Image
        fields = (
            'id',
            'name',
            'image',
        )


class LogoSerializer(serializers.ModelSerializer):
    logo = serializers.ReadOnlyField(source='get_absolute_logo_url')

    class Meta:
        model = models.Image
        fields = (
            'id',
            'name',
            'logo',
        )


class IconDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.IconData
        fields = (
            'id',
            'title',
            'icon',
            'data',
            'link',
        )


class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Video
        fields = (
            'id',
            'title',
            'embed_url_src',
        )


class ResourceSerializer(serializers.ModelSerializer):
    file = serializers.ReadOnlyField(source='get_absolute_file_url')

    class Meta:
        model = models.Resource
        fields = (
            'id',
            'title',
            'file',
        )


class TwitterFeedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TwitterFeed
        fields = (
            'id',
            'type',
            'link'
        )
# _____________________________________________________________________________________________________________________
