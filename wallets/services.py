from decimal import Decimal, InvalidOperation

from django.utils import timezone

from categories.models import Category
from transactions.models import Transaction


def get_wallet_auto_category(user, name, applies_to='BOTH'):
    category, _ = Category.objects.get_or_create(
        user=user,
        name=name,
        parent=None,
        defaults={
            'applies_to': applies_to,
            'is_active': True,
        },
    )
    return category


def decimal_from_value(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("El monto ingresado no es válido.")


def wallet_available_for_expense(wallet, existing_transaction=None):
    available = Decimal(wallet.current_balance)
    if (
        existing_transaction
        and existing_transaction.pk
        and existing_transaction.wallet_id == wallet.id
        and existing_transaction.type == 'EXPENSE'
    ):
        available += existing_transaction.amount
    return available


def wallet_can_cover_expense(wallet, amount, existing_transaction=None):
    if wallet.type == 'CREDIT':
        return True
    return decimal_from_value(amount) <= wallet_available_for_expense(wallet, existing_transaction)


def insufficient_balance_message(wallet, amount, existing_transaction=None):
    available = wallet_available_for_expense(wallet, existing_transaction)
    return f"Saldo insuficiente en {wallet.name}. Disponible: {available}; intento: {amount}."


def transaction_effect(tx_type, amount):
    amount = decimal_from_value(amount)
    if tx_type == 'INCOME':
        return amount
    if tx_type == 'EXPENSE':
        return -amount
    return Decimal('0')


def transaction_keeps_wallets_non_negative(wallet, tx_type, amount, existing_transaction=None):
    if wallet.type == 'CREDIT':
        return True, ''

    new_wallet_balance = Decimal(wallet.current_balance)
    old_wallet = None
    old_wallet_balance = None

    if existing_transaction and existing_transaction.pk:
        old_wallet = existing_transaction.wallet
        if old_wallet.type != 'CREDIT':
            old_wallet_balance = Decimal(old_wallet.current_balance) - transaction_effect(
                existing_transaction.type,
                existing_transaction.amount,
            )
            if old_wallet.pk == wallet.pk:
                new_wallet_balance = old_wallet_balance

    final_new_balance = new_wallet_balance + transaction_effect(tx_type, amount)
    if final_new_balance < 0:
        return False, f"El movimiento dejaría la cuenta {wallet.name} con saldo negativo ({final_new_balance})."

    if old_wallet and old_wallet.pk != wallet.pk and old_wallet.type != 'CREDIT' and old_wallet_balance < 0:
        return False, f"Editar este movimiento dejaría la cuenta {old_wallet.name} con saldo negativo ({old_wallet_balance})."

    return True, ''


def transaction_delete_keeps_wallet_non_negative(transaction):
    wallet = transaction.wallet
    if wallet.type == 'CREDIT':
        return True, ''

    final_balance = Decimal(wallet.current_balance) - transaction_effect(transaction.type, transaction.amount)
    if final_balance < 0:
        return False, f"Borrar este movimiento dejaría la cuenta {wallet.name} con saldo negativo ({final_balance})."
    return True, ''


def create_balance_adjustment(user, wallet, target_balance):
    if wallet.type == 'CREDIT':
        raise ValueError("Las tarjetas de crédito se ajustan registrando cargos o pagos, no saldo directo.")

    target = decimal_from_value(target_balance)
    if target < 0:
        raise ValueError("El saldo objetivo no puede ser negativo.")

    current = Decimal(wallet.current_balance)
    difference = target - current
    if difference == 0:
        return None, difference

    tx_type = 'INCOME' if difference > 0 else 'EXPENSE'
    amount = abs(difference)
    category = get_wallet_auto_category(user, 'Ajuste de saldo')

    tx = Transaction.objects.create(
        user=user,
        wallet=wallet,
        category=category,
        type=tx_type,
        subtype='UNIQUE' if tx_type == 'INCOME' else 'NORMAL',
        amount=amount,
        date=timezone.localdate(),
        description=f"Ajuste de saldo - {wallet.name}",
    )
    return tx, difference
