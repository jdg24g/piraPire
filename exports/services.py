import csv
import io
from transactions.models import Transaction


def generate_transactions_csv(user, filters=None):
    if filters is None:
        filters = {}

    # Filtrar transacciones del usuario
    qs = Transaction.objects.filter(user=user).select_related('category', 'category__parent', 'wallet')

    # Aplicar filtros
    date_from = filters.get('date_from')
    if date_from:
        qs = qs.filter(date__gte=date_from)

    date_to = filters.get('date_to')
    if date_to:
        qs = qs.filter(date__lte=date_to)

    wallet = filters.get('wallet')
    if wallet:
        qs = qs.filter(wallet_id=wallet)

    category = filters.get('category')
    if category:
        qs = qs.filter(category_id=category)

    tx_type = filters.get('type')
    if tx_type:
        qs = qs.filter(type=tx_type)

    subtype = filters.get('subtype')
    if subtype:
        qs = qs.filter(subtype=subtype)

    # Crear el stream en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escribir cabecera
    writer.writerow(['fecha', 'tipo', 'monto', 'categoria', 'subcategoria', 'cuenta', 'descripcion'])

    # Escribir filas
    for tx in qs:
        # Lógica de categorías y subcategorías
        if tx.category.parent:
            cat_name = tx.category.parent.name
            subcat_name = tx.category.name
        else:
            cat_name = tx.category.name
            subcat_name = ''

        writer.writerow([
            tx.date.strftime('%Y-%m-%d'),
            tx.type,
            float(tx.amount),
            cat_name,
            subcat_name,
            tx.wallet.name,
            tx.description or ''
        ])

    return output.getvalue()
