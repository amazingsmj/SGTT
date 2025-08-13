from rest_framework.routers import DefaultRouter
from .views import SettingViewSet

router = DefaultRouter()
router.register(r'settings', SettingViewSet, basename='setting')

urlpatterns = router.urls