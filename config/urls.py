from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

# Importaciones de vistas web
from accounts.web_views import WebLoginView, WebRegisterView, web_logout_view
from reports.web_views import WebDashboardView, WebReportView
from transactions.web_views import TransactionListView, TransactionCreateView, TransactionUpdateView, TransactionDeleteView
from wallets.web_views import WalletListView, WalletCreateView, WalletUpdateView, CreditCardPaymentView
from categories.web_views import CategoryListView, CategoryCreateView, CategoryUpdateView
from installments.web_views import InstallmentPurchaseListView, InstallmentPurchaseCreateView, InstallmentPurchaseUpdateView, InstallmentPurchasePayView, InstallmentSheetView, FixedExpensePayView, FixedExpenseDeactivateView, FixedExpenseUpdateView, FixedExpenseDeleteView

# ponytail: vista para redirigir la raíz del sitio
def root_redirect_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('config.api_urls')),
    
    # Rutas Web Frontend
    path('', root_redirect_view, name='root'),
    path('login/', WebLoginView.as_view(), name='login'),
    path('register/', WebRegisterView.as_view(), name='register'),
    path('logout/', web_logout_view, name='logout'),
    
    path('dashboard/', WebDashboardView.as_view(), name='dashboard'),
    
    path('movements/', TransactionListView.as_view(), name='transaction_list'),
    path('movements/new/', TransactionCreateView.as_view(), name='transaction_create'),
    path('movements/<int:pk>/edit/', TransactionUpdateView.as_view(), name='transaction_edit'),
    path('movements/<int:pk>/delete/', TransactionDeleteView.as_view(), name='transaction_delete'),
    
    path('wallets/', WalletListView.as_view(), name='wallet_list'),
    path('wallets/new/', WalletCreateView.as_view(), name='wallet_create'),
    path('wallets/<int:pk>/edit/', WalletUpdateView.as_view(), name='wallet_edit'),
    path('wallets/<int:pk>/pay-credit-card/', CreditCardPaymentView.as_view(), name='wallet_pay_credit_card'),
    
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/new/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_edit'),
    
    path('installments/', InstallmentPurchaseListView.as_view(), name='installment_list'),
    path('installments/sheet/', InstallmentSheetView.as_view(), name='installment_sheet'),
    path('installments/new/', InstallmentPurchaseCreateView.as_view(), name='installment_create'),
    path('installments/<int:pk>/edit/', InstallmentPurchaseUpdateView.as_view(), name='installment_edit'),
    path('installments/<int:pk>/pay/', InstallmentPurchasePayView.as_view(), name='installment_pay'),
    path('fixed-expenses/<int:pk>/edit/', FixedExpenseUpdateView.as_view(), name='fixed_expense_edit'),
    path('fixed-expenses/<int:pk>/delete/', FixedExpenseDeleteView.as_view(), name='fixed_expense_delete'),
    path('fixed-expenses/<int:pk>/pay/', FixedExpensePayView.as_view(), name='fixed_expense_pay'),
    path('fixed-expenses/<int:pk>/deactivate/', FixedExpenseDeactivateView.as_view(), name='fixed_expense_deactivate'),
    
    path('reports/', WebReportView.as_view(), name='report_list'),
]

# ponytail: servir archivos estáticos y media en base a la configuración dinámica del .env
if getattr(settings, 'PIRAPIRE_SERVE_STATIC', True):
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if getattr(settings, 'PIRAPIRE_SERVE_MEDIA', True):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
