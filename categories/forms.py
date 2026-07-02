# ponytail: formulario simple para Category filtrando categorías padre permitidas
from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'applies_to', 'parent', 'is_active']
        labels = {
            'name': 'Nombre de la Categoría',
            'applies_to': 'Aplica a',
            'parent': 'Categoría Padre (Opcional)',
            'is_active': 'Activa',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md'}),
            'applies_to': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-slate-800 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-purple-500'}),
            'parent': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-slate-800 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-purple-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded bg-white/10 border-white/20 text-purple-600 focus:ring-purple-500 h-5 w-5'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Solo permitir categorías del usuario o por defecto como categorías padre
            self.fields['parent'].queryset = Category.objects.filter(
                models.Q(user=user) | models.Q(is_default=True)
            ).exclude(id=self.instance.id if self.instance.id else -1)
