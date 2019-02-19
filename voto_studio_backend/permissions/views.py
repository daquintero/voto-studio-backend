from django.shortcuts import get_object_or_404
from rest_framework import authentication, status
from rest_framework.response import Response
from rest_framework.views import APIView
from voto_studio_backend.forms.views import get_model
from voto_studio_backend.permissions.shortcuts import get_object_or_403
from voto_studio_backend.users.models import User
from voto_studio_backend.users.serializers import UserSerializer


class GetUserPermissions(APIView):
    authentication_classes = (authentication.TokenAuthentication,)

    @staticmethod
    def get(request):
        model_label = request.GET.get('ml')
        instance_id = request.GET.get('id')

        model_class = get_model(model_label=model_label)
        instance = get_object_or_403(model_class, (request.user, 'write'), id=instance_id)

        permitted_users = [instance.user, *instance.permitted_users.all()]
        permissions_dict = instance.permissions_dict
        owner = instance.user

        response = {
            'owner': UserSerializer(owner).data,
            'permitted_users': UserSerializer(permitted_users, many=True).data,
            'permissions_dict': permissions_dict,
        }

        return Response(response, status=status.HTTP_200_OK)


class UpdateUserPermission(APIView):
    authentication_classes = (authentication.TokenAuthentication,)

    @staticmethod
    def post(request):
        model_label = request.data['model_label']
        instance_id = request.data['instance_id']

        model_class = get_model(model_label=model_label)
        instance = get_object_or_403(model_class, (request.user, 'write'), id=instance_id)

        user_id = request.data['user_id']
        permission_level = request.data['permission_level']
        update_type = request.data['update_type']

        user = get_object_or_404(User, id=user_id)
        if update_type == 'permit':
            instance.set_permission_level(user, permission_level)
        elif update_type == 'revoke':
            instance.revoke_user(user)

        response = {
            'id': user_id,
            'update_type': update_type,
            'permissions_dict': instance.permissions_dict,
        }

        return Response(response, status=status.HTTP_200_OK)
