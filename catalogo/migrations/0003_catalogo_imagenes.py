import json
from pathlib import Path

from django.db import migrations, models


def cargar_catalogo_inicial(apps, schema_editor):
    Producto = apps.get_model('catalogo', 'Producto')
    ruta_datos = Path(__file__).resolve().parent.parent / 'data' / 'productos_iniciales.json'
    with ruta_datos.open(encoding='utf-8') as archivo:
        productos = json.load(archivo)

    for producto in productos:
        Producto.objects.using(schema_editor.connection.alias).get_or_create(
            nombre=producto['nombre'],
            categoria=producto['categoria'],
            defaults={
                'precio': producto['precio'],
                'stock': producto['stock'],
                'imagen': producto['imagen'],
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0002_alter_producto_precio_alter_producto_stock_compra'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='imagen',
            field=models.URLField(blank=True, max_length=1000),
        ),
        migrations.RunPython(cargar_catalogo_inicial, migrations.RunPython.noop),
    ]
