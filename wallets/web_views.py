# ponytail: vistas web CRUD sencillas usando Class-Based Views de Django para billeteras
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Wallet
from .forms import WalletForm

class WalletListView(LoginRequiredMixin, ListView):
    model = Wallet
    template_name = 'wallets/list.html'
    context_object_name = 'wallets'

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

class WalletCreateView(LoginRequiredMixin, CreateView):
    model = Wallet
    form_class = WalletForm
    template_name = 'wallets/form.html'
    success_url = reverse_lazy('wallet_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Cuenta creada exitosamente.")
        return super().form_valid(form)

class WalletUpdateView(LoginRequiredMixin, UpdateView):
    model = Wallet
    form_class = WalletForm
    template_name = 'wallets/form.html'
    success_url = reverse_lazy('wallet_list')

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Cuenta actualizada exitosamente.")
        return super().form_valid(form)
