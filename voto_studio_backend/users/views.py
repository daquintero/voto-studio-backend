from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import authentication
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from . import models
from . import serializers


class UserDetailAPI(APIView):
    authentication_classes = (authentication.TokenAuthentication,)

    @staticmethod
    def get(request, **kwargs):
        if not request.user.is_authenticated:
            return Response('User not authenticated', status=status.HTTP_401_UNAUTHORIZED)

        user = get_object_or_404(models.User, id=request.GET.get('id'))
        user_data = serializers.UserSerializer(user).data
        type = kwargs.get('type')

        if type == 'full':
            return Response({'user': user_data}, status=status.HTTP_200_OK)
        elif type == 'email':
            return Response({'email': user_data['email']}, status=status.HTTP_200_OK)


class RegisterUserAPI(APIView):
    @staticmethod
    def post(request):
        user_serializer = serializers.UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            if user:
                user_data = serializers.UserSerializer(user).data
                token = Token.objects.create(user=user)
                user.save(using=settings.MAIN_SITE_DB)

                return Response({'user': {**user_data, 'token': token.key}}, status=status.HTTP_201_CREATED)

        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserAPI(APIView):
    @staticmethod
    def post(request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Please provide both an email and a password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password)
        if not user:
            return Response(
                {'error': 'Email and password do not match'},
                status=status.HTTP_404_NOT_FOUND
            )
        token, _ = Token.objects.get_or_create(user=user)
        user_data = serializers.UserSerializer(user).data

        return Response(
            {'user': {**user_data, 'token': token.key}},
            status=status.HTTP_200_OK
        )


class UserListAPI(APIView):
    @staticmethod
    def get(request):
        search_term = request.GET.get('search')
        if search_term is not '':
            users = models.User.search.filter(search=search_term, must_not={'id': request.user.id})
        else:
            users = []

        response = {
            'users': users,
        }

        return Response(response, status=status.HTTP_200_OK)
