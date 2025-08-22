from django.shortcuts import render
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.core.cache import cache
from .serializers import UserSerializer, UserCreateSerializer

User = get_user_model()


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.action in ['create']:
            return UserCreateSerializer
        return UserSerializer


class MeView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email requis'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Si le compte existe, un email a été envoyé.'})
        token = get_random_string(32)
        cache.set(f'pwd-reset:{token}', user.id, timeout=60 * 30)
        reset_link = request.build_absolute_uri(f"/reset-password?token={token}")
        send_mail(
            subject='Réinitialisation du mot de passe',
            message=f'Cliquez sur le lien pour réinitialiser votre mot de passe: {reset_link}',
            from_email=None,
            recipient_list=[email],
        )
        return Response({'detail': 'Si le compte existe, un email a été envoyé.'})


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        if not token or not new_password:
            return Response({'detail': 'Paramètres manquants'}, status=status.HTTP_400_BAD_REQUEST)
        user_id = cache.get(f'pwd-reset:{token}')
        if not user_id:
            return Response({'detail': 'Token invalide ou expiré'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(id=user_id)
        user.set_password(new_password)
        user.save(update_fields=['password'])
        cache.delete(f'pwd-reset:{token}')
        return Response({'detail': 'Mot de passe mis à jour'})
