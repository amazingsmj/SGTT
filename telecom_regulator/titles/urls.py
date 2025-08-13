from rest_framework.routers import DefaultRouter
from .views import TitreViewSet

router = DefaultRouter()
router.register(r'', TitreViewSet, basename='titre')

urlpatterns = router.urls