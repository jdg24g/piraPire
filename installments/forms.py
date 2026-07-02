# ponytail: formulario simple para InstallmentPurchase con filtros para wallet y category
from django import forms
from django.db.models import Q
from django.utils import timezone
from .models import InstallmentPurchase
from recurrences.models import RecurrentMovement
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
            'start_date': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'type': 'date'}),
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
        self.fields['total_installments'].required = False
        self.fields['paid_installments'].required = False
        self.fields['start_date'].required = False
        self.fields['status'].required = False

    def clean(self):
        cleaned_data = super().clean()
        entry_type = self.data.get('entry_type')
        total_amount = cleaned_data.get('total_amount')
        total_installments = cleaned_data.get('total_installments')
        installment_value = cleaned_data.get('installment_value')
        paid_installments = cleaned_data.get('paid_installments') or 0

        if entry_type in ['fijo', 'fijo_variable']:
            try:
                due_day = int(self.data.get('due_day', ''))
            except (TypeError, ValueError):
                due_day = None
            if not due_day or due_day < 1 or due_day > 31:
                raise forms.ValidationError("Debes proporcionar un día de vencimiento entre 1 y 31.")
            if entry_type == 'fijo' and not installment_value:
                raise forms.ValidationError("Debes proporcionar el monto mensual del gasto fijo.")
            cleaned_data['total_installments'] = 1
            cleaned_data['paid_installments'] = 0
            cleaned_data['total_amount'] = installment_value or 0
            cleaned_data['start_date'] = cleaned_data.get('start_date') or timezone.localdate()
            cleaned_data['status'] = 'ACTIVE'
            return cleaned_data

        if not total_installments:
            raise forms.ValidationError("Debes proporcionar la cantidad de cuotas.")

        if not cleaned_data.get('start_date'):
            raise forms.ValidationError("Debes proporcionar la fecha de inicio.")

        cleaned_data['status'] = cleaned_data.get('status') or 'ACTIVE'

        if total_installments and paid_installments > total_installments:
            raise forms.ValidationError("Las cuotas pagadas no pueden superar la cantidad total de cuotas.")

        if not total_amount:
            if not installment_value or not total_installments:
                raise forms.ValidationError("Debes proporcionar el Monto Total o el Valor Mensual junto con la Cantidad de Cuotas.")
            cleaned_data['total_amount'] = installment_value * total_installments

        return cleaned_data


class FixedExpenseForm(forms.ModelForm):
    class Meta:
        model = RecurrentMovement
        fields = ['description', 'wallet', 'category', 'amount', 'amount_is_variable', 'due_day', 'is_active']
        labels = {
            'description': 'Nombre del Gasto',
            'wallet': 'Cuenta para el Pago',
            'category': 'Categoría',
            'amount': 'Monto Mensual',
            'amount_is_variable': 'Monto variable mensual',
            'due_day': 'Día de Vencimiento',
            'is_active': 'Activo',
        }
        widgets = {
            'description': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md'}),
            'wallet': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-slate-800 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-purple-500'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-slate-800 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-purple-500'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'step': '0.01'}),
            'amount_is_variable': forms.CheckboxInput(attrs={'class': 'h-5 w-5 rounded border-white/20 bg-white/10 text-purple-600 focus:ring-purple-500'}),
            'due_day': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'min': '1', 'max': '31'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-5 w-5 rounded border-white/20 bg-white/10 text-purple-600 focus:ring-purple-500'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['wallet'].queryset = Wallet.objects.filter(user=user, is_active=True)
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(is_default=True)
            ).filter(is_active=True)
        self.fields['amount'].required = False

    def clean_due_day(self):
        due_day = self.cleaned_data.get('due_day')
        if not due_day or due_day < 1 or due_day > 31:
            raise forms.ValidationError("El día de vencimiento debe estar entre 1 y 31.")
        return due_day

    def clean(self):
        cleaned_data = super().clean()
        amount_is_variable = cleaned_data.get('amount_is_variable')
        amount = cleaned_data.get('amount')
        if amount_is_variable:
            cleaned_data['amount'] = 0
        elif not amount or amount <= 0:
            raise forms.ValidationError("Debes proporcionar el monto mensual del gasto fijo.")
        return cleaned_data
