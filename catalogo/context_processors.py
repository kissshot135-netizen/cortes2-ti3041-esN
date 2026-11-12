def carrito_total(request):
    carrito = request.session.get('carrito', {})
    total = sum(
        cantidad
        for cantidad in carrito.values()
        if isinstance(cantidad, int) and cantidad > 0
    )
    return {'carrito_total': total}
