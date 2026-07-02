from django.db import migrations


def create_default_categories(apps, schema_editor):
    Category = apps.get_model('categories', 'Category')
    
    defaults = [
        ('Alimentación', 'EXPENSE'),
        ('Transporte', 'EXPENSE'),
        ('Hogar', 'EXPENSE'),
        ('Servicios', 'EXPENSE'),
        ('Salud', 'EXPENSE'),
        ('Educación', 'EXPENSE'),
        ('Entretenimiento', 'EXPENSE'),
        ('Tecnología', 'EXPENSE'),
        ('Vehículo', 'EXPENSE'),
        ('Mascotas', 'EXPENSE'),
        ('Impuestos', 'BOTH'),
        ('Otros', 'BOTH'),
        ('Sueldo', 'INCOME'),
        ('Ventas', 'INCOME'),
        ('Inversiones', 'INCOME'),
    ]
    
    for name, applies_to in defaults:
        Category.objects.get_or_create(
            name=name,
            defaults={
                'applies_to': applies_to,
                'is_default': True,
                'user': None
            }
        )


def remove_default_categories(apps, schema_editor):
    Category = apps.get_model('categories', 'Category')
    Category.objects.filter(is_default=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_categories, remove_default_categories),
    ]
