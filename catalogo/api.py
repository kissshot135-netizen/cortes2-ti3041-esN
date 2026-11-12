import json
from json import JSONDecodeError

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from .forms import ColeccionForm, ContactoForm, ProductoForm
from .models import Coleccion, Contacto, Producto


def _producto_json(producto):
    return {
        'id': producto.pk,
        'nombre': producto.nombre,
        'categoria': producto.categoria,
        'precio': producto.precio,
        'stock': producto.stock,
        'imagen': producto.imagen,
        'colecciones': [coleccion.pk for coleccion in producto.colecciones.all()],
    }


def _coleccion_json(coleccion):
    return {
        'id': coleccion.pk,
        'nombre': coleccion.nombre,
        'descripcion': coleccion.descripcion,
        'productos': [producto.pk for producto in coleccion.productos.all()],
        'creada_en': coleccion.creada_en.isoformat(),
    }


def _contacto_json(contacto):
    return {
        'id': contacto.pk,
        'nombre': contacto.nombre,
        'email': contacto.email,
        'telefono': contacto.telefono,
        'asunto': contacto.asunto,
        'mensaje': contacto.mensaje,
        'creado_en': contacto.creado_en.isoformat(),
        'respondido': contacto.respondido,
    }


def _staff_permission(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Autenticación requerida.'}, status=401)
    if not request.user.is_staff:
        return JsonResponse({'detail': 'Se requieren permisos de administrador.'}, status=403)
    return None


def _json_payload(request):
    try:
        payload = json.loads(request.body)
    except (JSONDecodeError, UnicodeDecodeError):
        return None, JsonResponse(
            {'detail': 'El cuerpo debe contener JSON válido.'},
            status=400,
        )
    if not isinstance(payload, dict):
        return None, JsonResponse(
            {'detail': 'El cuerpo JSON debe ser un objeto.'},
            status=400,
        )
    return payload, None


def _form_errors(form):
    return JsonResponse({'errors': form.errors.get_json_data()}, status=400)


@require_http_methods(['GET'])
def api_root(request):
    return JsonResponse(
        {
            'productos': '/api/v1/productos/',
            'colecciones': '/api/v1/colecciones/',
            'contactos': '/api/v1/contactos/',
        }
    )


@require_http_methods(['GET', 'POST'])
def api_productos(request):
    if request.method == 'GET':
        productos = Producto.objects.prefetch_related('colecciones').order_by('nombre')
        return JsonResponse({'results': [_producto_json(p) for p in productos]})

    permission_error = _staff_permission(request)
    if permission_error:
        return permission_error

    payload, payload_error = _json_payload(request)
    if payload_error:
        return payload_error
    form = ProductoForm(payload)
    if not form.is_valid():
        return _form_errors(form)

    producto = form.save()
    return JsonResponse(_producto_json(producto), status=201)


@require_http_methods(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_producto_detalle(request, producto_id):
    if request.method != 'GET':
        permission_error = _staff_permission(request)
        if permission_error:
            return permission_error

    producto = get_object_or_404(
        Producto.objects.prefetch_related('colecciones'),
        pk=producto_id,
    )
    if request.method == 'GET':
        return JsonResponse(_producto_json(producto))

    if request.method == 'DELETE':
        producto.delete()
        return HttpResponse(status=204)

    payload, payload_error = _json_payload(request)
    if payload_error:
        return payload_error
    if request.method == 'PATCH':
        payload = {
            'nombre': producto.nombre,
            'categoria': producto.categoria,
            'precio': producto.precio,
            'stock': producto.stock,
            'imagen': producto.imagen,
            **payload,
        }
    form = ProductoForm(payload, instance=producto)
    if not form.is_valid():
        return _form_errors(form)

    return JsonResponse(_producto_json(form.save()))


@require_http_methods(['GET', 'POST'])
def api_colecciones(request):
    if request.method == 'GET':
        colecciones = Coleccion.objects.prefetch_related('productos').order_by('nombre')
        return JsonResponse({'results': [_coleccion_json(c) for c in colecciones]})

    permission_error = _staff_permission(request)
    if permission_error:
        return permission_error

    payload, payload_error = _json_payload(request)
    if payload_error:
        return payload_error
    form = ColeccionForm(payload)
    if not form.is_valid():
        return _form_errors(form)

    return JsonResponse(_coleccion_json(form.save()), status=201)


@require_http_methods(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_coleccion_detalle(request, coleccion_id):
    if request.method != 'GET':
        permission_error = _staff_permission(request)
        if permission_error:
            return permission_error

    coleccion = get_object_or_404(
        Coleccion.objects.prefetch_related('productos'),
        pk=coleccion_id,
    )
    if request.method == 'GET':
        return JsonResponse(_coleccion_json(coleccion))

    if request.method == 'DELETE':
        coleccion.delete()
        return HttpResponse(status=204)

    payload, payload_error = _json_payload(request)
    if payload_error:
        return payload_error
    if request.method == 'PATCH':
        payload = {
            'nombre': coleccion.nombre,
            'descripcion': coleccion.descripcion,
            'productos': [producto.pk for producto in coleccion.productos.all()],
            **payload,
        }
    form = ColeccionForm(payload, instance=coleccion)
    if not form.is_valid():
        return _form_errors(form)

    return JsonResponse(_coleccion_json(form.save()))


@require_http_methods(['GET', 'POST'])
def api_contactos(request):
    if request.method == 'GET':
        permission_error = _staff_permission(request)
        if permission_error:
            return permission_error
        contactos = Contacto.objects.order_by('-creado_en')
        return JsonResponse({'results': [_contacto_json(c) for c in contactos]})

    payload, payload_error = _json_payload(request)
    if payload_error:
        return payload_error
    form = ContactoForm(payload)
    if not form.is_valid():
        return _form_errors(form)

    return JsonResponse(_contacto_json(form.save()), status=201)
