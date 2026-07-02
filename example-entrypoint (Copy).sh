#!/bin/bash
set -e

echo "============================================================"
echo "  gtcarshop - iniciando contenedor"
echo "============================================================"

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
username = '${DJANGO_SUPERUSER_USERNAME:-admin}'
email = '${DJANGO_SUPERUSER_EMAIL:-admin@gtcarshop.local}'
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password='${DJANGO_SUPERUSER_PASSWORD}')
    print(f'Superusuario {username} creado.')
else:
    print(f'Superusuario {username} ya existe.')
" || echo "Aviso: no se pudo crear/verificar el superusuario."
fi

exec daphne -b 0.0.0.0 -p 8000 a_core.asgi:application
