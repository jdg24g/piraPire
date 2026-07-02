from rest_framework import viewsets, permissions
from .models import RecurrentMovement
from .serializers import RecurrentMovementSerializer


class RecurrentMovementViewSet(viewsets.ModelViewSet):
    serializer_class = RecurrentMovementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['wallet', 'category', 'type', 'frequency', 'is_active']

    def get_queryset(self):
        return RecurrentMovement.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
