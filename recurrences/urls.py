from rest_framework.routers import DefaultRouter
from .views import RecurrentMovementViewSet

router = DefaultRouter()
router.register('', RecurrentMovementViewSet, basename='recurrence')

urlpatterns = router.urls
