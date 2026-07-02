# ponytail: formulario simple para InstallmentPurchase con filtros para wallet y category
from django import forms
from django.db.models import Q
from .models import InstallmentPurchase
from wallets.models import Wallet
from categories.models import Category

class InstallmentPurchaseForm(forms.ModelForm):
    class Meta:
        model = InstallmentPurchase
        fields = ['product_name', 'wallet', 'category', 'total_amount', 'total_installments', 'installment_value', 'paid_installments', 'start_date', 'status']
        labels = {
            'product_name': 'Producto / Servicio',
            'wallet': 'Cuenta para el Pago',
            'category': 'Categoría',
            'total_amount': 'Monto Total',
            'total_installments': 'Cantidad de Cuotas (o Meses)',
            'installment_value': 'Valor de Cuota (o Mensualidad)',
            'paid_installments': 'Cuotas Pagadas',
            'start_date': 'Fecha de Inicio',
            'status': 'Estado',
        }
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md'}),
            'wallet': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-slate-800 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-purple-500'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-slate-800 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-purple-500'}),
            'total_amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'step': '0.01'}),
            'total_installments': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md'}),
            'installment_value': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'step': '0.01'}),
            'paid_installments': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md'}),
            'start_date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-slate-800 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-purple-500'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filtrar wallets del usuario y activas
            self.fields['wallet'].queryset = Wallet.objects.filter(user=user, is_active=True)
            # Filtrar categorías del usuario o predeterminadas del sistema y que estén activas
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(is_default=True)
            ).filter(is_active=True)

        # Hacemos que el Monto Total sea opcional desde el formulario para permitir cálculos inversos
        self.fields['total_amount'].required = False
        self.fields['installment_value'].required = False

    def clean(self):
        cleaned_data = super().clean()
        total_amount = cleaned_data.get('total_amount')
        total_installments = cleaned_data.get('total_installments')
        installment_value = cleaned_data.get('installment_value')

        if not total_amount:
            if not installment_value or not total_installments:
                raise forms.ValidationError("Debes proporcionar el Monto Total o el Valor Mensual junto con la Cantidad de Cuotas.")
            cleaned_data['total_amount'] = installment_value * total_installments

        return cleaned_data
