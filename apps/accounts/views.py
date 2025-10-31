# apps/accounts/views.py   (DRF)
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

from .models import User, Group,CompanyUnit,Division, Department, Section, SubSection, Floor,Line, Designation
from .serializers import (
    UserSerializer, DepartmentSerializer,
    DesignationSerializer, LoginSerializer,
    RegisterSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_hr:
            return User.objects.all()
        elif user.is_manager:
            return User.objects.filter(role='EMPLOYEE')
        else:
            return User.objects.filter(id=user.id)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        # create/update/delete only for admins/hr
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class DesignationViewSet(viewsets.ModelViewSet):
    serializer_class = DesignationSerializer

    def get_queryset(self):
        qs = Designation.objects.filter(is_active=True)
        department_id = self.request.query_params.get('department_id')
        if department_id:
            qs = qs.filter(department_id=department_id)
        return qs


# ----- Auth endpoints for API -----
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        password = data.pop('password')
        # create user via manager to ensure hashing and required fields
        user = User.objects.create(
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            username=data.get('username', data.get('email')),
            password=make_password(password),
            role=data.get('role', 'EMPLOYEE'),
            is_active=True
        )
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {'refresh': str(refresh), 'access': str(refresh.access_token)}
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.is_active:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Login successful',
                    'user': UserSerializer(user).data,
                    'tokens': {'refresh': str(refresh), 'access': str(refresh.access_token)}
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Account is disabled'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_logout_view(request):
    refresh_token = request.data.get('refresh_token')
    if not refresh_token:
        return Response({'error': 'Refresh token required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
    except Exception:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_profile_view(request):
    return Response(UserSerializer(request.user).data)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def api_update_profile_view(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Profile updated', 'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import CompanyUnit, CustomGroup

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_units_by_group(request):
    """Return all active units for a specific group"""
    try:
        group_id = request.GET.get('group_id')
        if not group_id:
            return Response({
                'status': 'error',
                'message': 'group_id is required'
            }, status=400)

        units = CompanyUnit.objects.filter(
            group_id=group_id,
            is_active=True
        ).values('id', 'name').order_by('name')
        
        return Response({
            'status': 'success',
            'units': list(units)
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=400)