from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import CompraForm, ProductoForm, RegistroConsumidorForm
from .models import Compra, Producto


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
@require_POST
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    nombre = producto.nombre
    producto.delete()
    messages.success(request, f'Se eliminó {nombre} del catálogo.')
    return redirect('gestionar_productos')
