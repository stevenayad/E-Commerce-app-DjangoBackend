from django.shortcuts import render
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.response import Response;
from .serializers import SignupSerializer, UserSerializer
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
def register(request):
    data = request.data
    serializer = SignupSerializer(data=data)

    
    if serializer.is_valid(): #Check on username already exists.
        if not User.objects.filter(email=data['email']).exists():
            user = User.objects.create_user(
                username=data['email'], 
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                password=data['password'],
            )
            print(user)
            return Response(
                {'details': 'Your account registered successfully!'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'This email already exists!'},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = UserSerializer(request.user)
    return Response(user.data)