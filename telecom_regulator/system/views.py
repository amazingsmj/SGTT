from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Setting
from .serializers import SettingSerializer
from common.permissions import IsAdmin


# Create your views here.

class SettingViewSet(viewsets.ModelViewSet):
    queryset = Setting.objects.all().order_by('key')
    serializer_class = SettingSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
