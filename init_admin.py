import os
import django

# Inicializar configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()
    # ponytail: leer variables prioritariamente con el prefijo PIRAPIRE_
    username = os.environ.get('PIRAPIRE_SUPERUSER_USERNAME', os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'))
    email = os.environ.get('PIRAPIRE_SUPERUSER_EMAIL', os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@pirapire.local'))
    password = os.environ.get('PIRAPIRE_SUPERUSER_PASSWORD', os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123'))
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superusuario '{username}' creado exitosamente.")
    else:
        print(f"El superusuario '{username}' ya existe.")

if __name__ == '__main__':
    create_admin()
