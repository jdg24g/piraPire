from rest_framework import serializers
from .models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    current_balance = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        read_only=True
    )
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Wallet
        fields = [
            'id', 'user', 'name', 'type', 'initial_balance', 
            'current_balance', 'currency', 'is_active', 
            'created_at', 'updated_at'
        ]
