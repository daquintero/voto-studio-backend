from rest_framework import serializers
from rest_framework import validators
from . import models


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(queryset=models.User.objects.all())]
    )
    name = serializers.CharField(min_length=2, max_length=32)
    password = serializers.CharField(min_length=8, write_only=True)
    profile_picture_url = serializers.SerializerMethodField()

    def create(self, validated_data):
        return models.User.objects.create_user(**validated_data)

    class Meta:
        model = models.User
        fields = (
            'id',
            'email',
            'name',
            'password',
            'profile_picture_url',
        )

    def get_profile_picture_url(self, obj):
        return obj.profile_picture.image.url if obj.profile_picture else '/media/images/default_profile_picture.jpg'
