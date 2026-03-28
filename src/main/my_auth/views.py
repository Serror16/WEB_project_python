from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema

from .serializers import RegisterSerializer, LoginSerializer, UserResponseSerializer, RefreshTokenSerializer


class RegisterView(generics.GenericAPIView):
    """
    API регистрации
    """

    permission_classes = [permissions.AllowAny]
    serializer = RegisterSerializer

    @extend_schema(
        summary="Регистрация нового пользователя",
        request=RegisterSerializer,
        responses={201: UserResponseSerializer}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserResponseSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'message': 'Регистрация успешна'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    """
    API входа
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    
    @extend_schema(
        summary="Вход в систему",
        request=LoginSerializer,
        responses={200: UserResponseSerializer}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserResponseSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'message': 'Вход успешен'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(generics.GenericAPIView):
    """
    API выхода
    """
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RefreshTokenSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        refresh_token = serializer.validated_data.get('refresh')
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Выход выполнен успешно'}, 
                          status=status.HTTP_200_OK)
        except TokenError:
            return Response({'error': 'Неверный refresh token'}, 
                          status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(generics.GenericAPIView):
    """
    API refresh токена
    """
    
    permission_classes = [permissions.AllowAny]
    serializer_class = RefreshTokenSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        refresh_token = serializer.validated_data.get('refresh')
        
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'error': 'Неверный или истекший refresh token'}, 
                          status=status.HTTP_401_UNAUTHORIZED)


class UserInfoView(APIView):
    """
    API информации о пользователе
    """
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserResponseSerializer