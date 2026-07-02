from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'user', 'name', 'applies_to', 'parent', 
            'parent_name', 'is_default', 'is_active'
        ]
        read_only_fields = ['is_default']

    def validate(self, data):
        # Evitar ciclo autorreferencial (una categoría no puede ser su propio padre)
        parent = data.get('parent')
        if parent and self.instance and parent.id == self.instance.id:
            raise serializers.ValidationError("Una categoría no puede ser su propio elemento padre.")
        return data
