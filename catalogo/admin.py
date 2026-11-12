from django.contrib import admin

from .models import Coleccion, Compra, Contacto, Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock')
    list_filter = ('categoria',)
    search_fields = ('nombre',)


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('nombre_producto', 'consumidor', 'cantidad', 'precio_unitario', 'fecha')
    list_filter = ('fecha',)
    search_fields = ('nombre_producto', 'consumidor__username')
    readonly_fields = ('consumidor', 'producto', 'nombre_producto', 'precio_unitario', 'cantidad', 'fecha')


@admin.register(Coleccion)
class ColeccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'creada_en')
    search_fields = ('nombre', 'descripcion')
    filter_horizontal = ('productos',)


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('asunto', 'nombre', 'email', 'creado_en', 'respondido')
    list_filter = ('respondido', 'creado_en')
    search_fields = ('nombre', 'email', 'asunto', 'mensaje')
    readonly_fields = ('creado_en',)