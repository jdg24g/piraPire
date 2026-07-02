from rest_framework.routers import DefaultRouter
from .views import InstallmentPurchaseViewSet

router = DefaultRouter()
router.register('', InstallmentPurchaseViewSet, basename='installment')

urlpatterns = router.urls
