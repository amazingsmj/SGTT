from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'nom', 'prenom', 'telephone', 'role',
            'entreprise', 'adresse', 'is_active', 'is_staff', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'is_active', 'is_staff', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'nom', 'prenom', 'telephone', 'role', 'entreprise', 'adresse', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user