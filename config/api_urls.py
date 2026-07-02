from django.urls import path, include

urlpatterns = [
    path('auth/', include('accounts.urls')),
    path('wallets/', include('wallets.urls')),
    path('categories/', include('categories.urls')),
    path('transactions/', include('transactions.urls')),
    path('installments/', include('installments.urls')),
    path('recurrences/', include('recurrences.urls')),
    path('reports/', include('reports.urls')),
    path('exports/', include('exports.urls')),
]

