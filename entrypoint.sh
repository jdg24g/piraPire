#!/bin/bash
set -e

echo "============================================================"
echo "  PiraPire - iniciando contenedor"
echo "============================================================"

echo "1. Verificando dependencias de Node (Tailwind)..."
if [ -d "node_modules" ]; then
    echo "Dependencias de Node ya instaladas en la imagen."
else
    npm install --no-fund --no-audit
fi

echo "2. Compilando Tailwind CSS..."
npm run build:css

echo "3. Ejecutando migraciones..."
python manage.py migrate --noinput

echo "4. Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "5. Configurando superusuario (si corresponde)..."
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py shell -c "
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.environ.get('PIRAPIRE_SUPERUSER_USERNAME', os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'))
email = os.environ.get('PIRAPIRE_SUPERUSER_EMAIL', os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@pirapire.local'))
password = os.environ.get('PIRAPIRE_SUPERUSER_PASSWORD', os.environ.get('DJANGO_SUPERUSER_PASSWORD'))

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superusuario {username} creado exitosamente.')
else:
    print(f'El superusuario {username} ya existe.')
" || echo "Aviso: no se pudo crear/verificar el superusuario."
fi

echo "6. Iniciando servidor Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
