from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.db.models import Count, F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import (
    ColeccionForm,
    CompraForm,
    ContactoForm,
    ProductoForm,
    RegistroConsumidorForm,
)
from .models import Coleccion, Compra, Producto


def inicio(request):
    return render(request, 'catalogo/inicio.html')


def lista_productos(request):
    productos = Producto.objects.order_by('nombre')
    return render(request, 'catalogo/index.html', {'productos': productos})


class IngresoView(LoginView):
    template_name = 'catalogo/ingreso.html'
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        if self.request.user.is_staff:
            return reverse('gestionar_productos')
        return reverse('inicio')


def registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    form = RegistroConsumidorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        consumidor = form.save()
        login(request, consumidor)
        messages.success(request, 'Tu cuenta de consumidor ya está lista.')
        return redirect('inicio')
    return render(request, 'catalogo/registro.html', {'form': form})


@login_required
@user_passes_test(lambda usuario: not usuario.is_staff)
@require_POST
def comprar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    form = CompraForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Indica una cantidad válida para comprar.')
        return redirect('lista_productos')

    cantidad = form.cleaned_data['cantidad']
    with transaction.atomic():
        producto = get_object_or_404(
            Producto.objects.select_for_update(),
            pk=producto_id,
        )
        if producto.stock < cantidad:
            messages.error(request, f'Stock insuficiente para {producto.nombre}.')
            return redirect('lista_productos')

        Compra.objects.create(
            consumidor=request.user,
            producto=producto,
            nombre_producto=producto.nombre,
            precio_unitario=producto.precio,
            cantidad=cantidad,
        )
        producto.stock -= cantidad
        producto.save(update_fields=['stock'])

    messages.success(request, f'Compra realizada: {cantidad} × {producto.nombre}.')
    return redirect('lista_productos')


def es_administrador(usuario):
    return usuario.is_authenticated and usuario.is_staff


@login_required
@user_passes_test(es_administrador)
def gestionar_productos(request):
    form = ProductoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        producto = form.save()
        messages.success(request, f'Se agregó {producto.nombre} al catálogo.')
        return redirect('gestionar_productos')

    productos = Producto.objects.order_by('nombre')
    compras = Compra.objects.select_related('consumidor').order_by('-fecha')[:10]
    return render(
        request,
        'catalogo/gestionar.html',
        {'form': form, 'productos': productos, 'compras': compras},
    )


@login_required
@user_passes_test(es_administrador)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    form = ProductoForm(request.POST or None, instance=producto)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Se actualizó {producto.nombre}.')
        return redirect('gestionar_productos')

    return render(
        request,
        'catalogo/editar_producto.html',
        {'form': form, 'producto': producto},
    )


@login_required
@user_passes_test(es_administrador)
@require_POST
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    nombre = producto.nombre
    producto.delete()
    messages.success(request, f'Se eliminó {nombre} del catálogo.')
    return redirect('gestionar_productos')


def lista_colecciones(request):
    colecciones = Coleccion.objects.prefetch_related('productos').order_by('nombre')
    return render(
        request,
        'catalogo/colecciones.html',
        {'colecciones': colecciones},
    )


@login_required
@user_passes_test(es_administrador)
def gestionar_colecciones(request):
    form = ColeccionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        coleccion = form.save()
        messages.success(request, f'Se creó la colección {coleccion.nombre}.')
        return redirect('gestionar_colecciones')

    colecciones = Coleccion.objects.prefetch_related('productos').order_by('nombre')
    return render(
        request,
        'catalogo/gestionar_colecciones.html',
        {'form': form, 'colecciones': colecciones},
    )


@login_required
@user_passes_test(es_administrador)
def editar_coleccion(request, coleccion_id):
    coleccion = get_object_or_404(Coleccion, pk=coleccion_id)
    form = ColeccionForm(request.POST or None, instance=coleccion)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Se actualizó la colección {coleccion.nombre}.')
        return redirect('gestionar_colecciones')

    return render(
        request,
        'catalogo/editar_coleccion.html',
        {'form': form, 'coleccion': coleccion},
    )


@login_required
@user_passes_test(es_administrador)
@require_POST
def eliminar_coleccion(request, coleccion_id):
    coleccion = get_object_or_404(Coleccion, pk=coleccion_id)
    nombre = coleccion.nombre
    coleccion.delete()
    messages.success(request, f'Se eliminó la colección {nombre}.')
    return redirect('gestionar_colecciones')


@login_required
@user_passes_test(es_administrador)
def reportes(request):
    productos_por_categoria = (
        Producto.objects.values('categoria')
        .annotate(
            cantidad_productos=Count('id'),
            stock_total=Sum('stock'),
            valor_inventario=Sum(F('precio') * F('stock')),
        )
        .order_by('categoria')
    )
    ventas_por_producto = (
        Compra.objects.values('nombre_producto')
        .annotate(
            unidades_vendidas=Sum('cantidad'),
            ingresos=Sum(F('precio_unitario') * F('cantidad')),
        )
        .order_by('-ingresos', 'nombre_producto')[:10]
    )
    return render(
        request,
        'catalogo/reportes.html',
        {
            'productos_por_categoria': productos_por_categoria,
            'ventas_por_producto': ventas_por_producto,
        },
    )


def formulario_contacto(request):
    form = ContactoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        contacto = form.save()
        messages.success(
            request,
            f'Gracias, {contacto.nombre}. Recibimos tu mensaje.',
        )
        return redirect('contacto')
    return render(request, 'catalogo/contacto.html', {'form': form})


@require_POST
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    form = CompraForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Indica una cantidad válida para agregar.')
        return redirect('lista_productos')

    carrito = request.session.get('carrito', {})
    clave_producto = str(producto.pk)
    cantidad = carrito.get(clave_producto, 0) + form.cleaned_data['cantidad']
    if cantidad > producto.stock:
        messages.error(
            request,
            f'Solo hay {producto.stock} unidades disponibles de {producto.nombre}.',
        )
        return redirect('lista_productos')

    carrito[clave_producto] = cantidad
    request.session['carrito'] = carrito
    messages.success(request, f'{producto.nombre} se agregó al carrito.')
    return redirect('lista_productos')


def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    productos = Producto.objects.filter(pk__in=carrito.keys()).order_by('nombre')
    items = []
    carrito_valido = {}
    for producto in productos:
        cantidad = carrito.get(str(producto.pk))
        if not isinstance(cantidad, int) or cantidad < 1:
            continue
        carrito_valido[str(producto.pk)] = cantidad
        items.append(
            {
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': producto.precio * cantidad,
            }
        )

    request.session['carrito'] = carrito_valido
    return render(
        request,
        'catalogo/carrito.html',
        {'items': items, 'total': sum(item['subtotal'] for item in items)},
    )


@require_POST
def quitar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    carrito.pop(str(producto_id), None)
    request.session['carrito'] = carrito
    messages.success(request, 'Se quitó el producto del carrito.')
    return redirect('ver_carrito')


@login_required
@require_POST
def finalizar_compra(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'El carrito está vacío.')
        return redirect('ver_carrito')

    with transaction.atomic():
        productos = list(
            Producto.objects.select_for_update().filter(pk__in=carrito.keys())
        )
        if len(productos) != len(carrito):
            messages.error(
                request,
                'El carrito contiene productos que ya no están disponibles.',
            )
            return redirect('ver_carrito')

        pedidos = []
        for producto in productos:
            cantidad = carrito.get(str(producto.pk))
            if not isinstance(cantidad, int) or cantidad < 1:
                messages.error(request, 'El carrito contiene una cantidad inválida.')
                return redirect('ver_carrito')
            if producto.stock < cantidad:
                messages.error(request, f'Stock insuficiente para {producto.nombre}.')
                return redirect('ver_carrito')
            pedidos.append((producto, cantidad))

        for producto, cantidad in pedidos:
            Compra.objects.create(
                consumidor=request.user,
                producto=producto,
                nombre_producto=producto.nombre,
                precio_unitario=producto.precio,
                cantidad=cantidad,
            )
            producto.stock -= cantidad
            producto.save(update_fields=['stock'])

    request.session['carrito'] = {}
    messages.success(request, 'Compra realizada. Gracias por tu pedido.')
    return redirect('lista_productos')
