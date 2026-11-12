from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import ContactoForm
from .models import Coleccion, Compra, Contacto, Producto


class CatalogoTests(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre='Martillo',
            categoria='Herramientas',
            precio=12000,
            stock=5,
        )
        self.consumidor = User.objects.create_user(
            username='consumidor',
            password='Password12345!',
        )
        self.administrador = User.objects.create_user(
            username='administrador',
            password='Password12345!',
            is_staff=True,
        )
        self.productos_iniciales = Producto.objects.count()

    def test_inicio_y_catalogo_cargan(self):
        self.assertEqual(self.client.get(reverse('inicio')).status_code, 200)
        respuesta = self.client.get(reverse('lista_productos'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Martillo')
        self.assertContains(respuesta, 'Martillo de acero 16 oz')
        self.assertContains(
            respuesta,
            'https://images.unsplash.com/photo-1679210208120-1b6a008be9b4',
        )
        self.assertContains(respuesta, 'row-cols-1')
        self.assertContains(respuesta, '/static/catalogo/imagen-no-disponible.svg')
        self.assertContains(respuesta, 'onerror=')

    def test_catalogo_muestra_imagen_del_producto_si_esta_disponible(self):
        self.producto.imagen = 'https://example.com/martillo.jpg'
        self.producto.save(update_fields=['imagen'])

        respuesta = self.client.get(reverse('lista_productos'))

        self.assertContains(respuesta, 'src="https://example.com/martillo.jpg"')

    def test_coleccion_guarda_relacion_many_to_many_con_productos(self):
        coleccion = Coleccion.objects.create(
            nombre='Herramientas esenciales',
            descripcion='Selección para el hogar',
        )
        coleccion.productos.add(self.producto)

        self.assertIn(self.producto, coleccion.productos.all())
        self.assertIn(coleccion, self.producto.colecciones.all())

    def test_formulario_contacto_valida_y_guarda_mensaje(self):
        form = ContactoForm(
            data={
                'nombre': 'Ana Pérez',
                'email': 'ana@example.com',
                'telefono': '',
                'asunto': 'Consulta',
                'mensaje': '¿Tienen stock?',
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        contacto = form.save()
        self.assertEqual(Contacto.objects.get(pk=contacto.pk).email, 'ana@example.com')

    def test_catalogo_muestra_productos_agotados(self):
        agotado = Producto.objects.create(
            nombre='Producto agotado',
            categoria='Herramientas',
            precio=1000,
            stock=0,
        )

        respuesta = self.client.get(reverse('lista_productos'))

        self.assertContains(respuesta, agotado.nombre)
        self.assertContains(respuesta, 'Agotado')
        self.assertContains(respuesta, 'Sin stock disponible')
        self.assertNotContains(
            respuesta,
            f'action="/catalogo/{agotado.pk}/comprar/"',
        )

    def test_superusuario_puede_gestionar_productos_en_admin(self):
        superusuario = User.objects.create_superuser(
            username='superusuario',
            email='superusuario@example.com',
            password='Password12345!',
        )
        self.client.force_login(superusuario)

        self.assertEqual(self.client.get('/admin/').status_code, 200)
        respuesta = self.client.get('/admin/catalogo/producto/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Martillo')

    def test_ingreso_redirige_segun_rol(self):
        self.assertEqual(self.client.get(reverse('ingreso')).status_code, 200)
        respuesta = self.client.post(
            reverse('ingreso'),
            {'username': 'consumidor', 'password': 'Password12345!'},
        )
        self.assertRedirects(respuesta, reverse('inicio'))

        self.client.logout()
        respuesta = self.client.post(
            reverse('ingreso'),
            {'username': 'administrador', 'password': 'Password12345!'},
        )
        self.assertRedirects(respuesta, reverse('gestionar_productos'))

    def test_registro_crea_cuenta_de_consumidor(self):
        self.assertEqual(self.client.get(reverse('registro')).status_code, 200)
        respuesta = self.client.post(
            reverse('registro'),
            {
                'username': 'nuevo',
                'email': 'nuevo@example.com',
                'password1': '1234',
                'password2': '1234',
            },
        )

        self.assertRedirects(respuesta, reverse('inicio'))
        usuario = User.objects.get(username='nuevo')
        self.assertFalse(usuario.is_staff)

    def test_consumidor_compra_y_se_actualiza_stock(self):
        self.client.force_login(self.consumidor)

        respuesta = self.client.post(
            reverse('comprar_producto', args=[self.producto.pk]),
            {'cantidad': 2},
        )

        self.assertRedirects(respuesta, reverse('lista_productos'))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        compra = Compra.objects.get()
        self.assertEqual(compra.consumidor, self.consumidor)
        self.assertEqual(compra.cantidad, 2)

    def test_compra_rechaza_cantidad_superior_al_stock(self):
        self.client.force_login(self.consumidor)

        self.client.post(
            reverse('comprar_producto', args=[self.producto.pk]),
            {'cantidad': 6},
        )

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 5)
        self.assertFalse(Compra.objects.exists())

    def test_solo_administrador_puede_agregar_y_eliminar_productos(self):
        url = reverse('gestionar_productos')
        self.client.force_login(self.consumidor)
        self.assertEqual(self.client.get(url).status_code, 302)
        self.assertEqual(self.client.post(url, {}).status_code, 302)
        self.assertEqual(Producto.objects.count(), self.productos_iniciales)

        self.client.force_login(self.administrador)
        self.assertEqual(self.client.get(url).status_code, 200)
        respuesta = self.client.post(
            url,
            {
                'nombre': 'Taladro',
                'categoria': 'Herramientas eléctricas',
                'precio': 45000,
                'stock': 4,
            },
        )
        self.assertRedirects(respuesta, url)
        taladro = Producto.objects.get(nombre='Taladro')

        respuesta = self.client.post(
            reverse('eliminar_producto', args=[taladro.pk]),
        )
        self.assertRedirects(respuesta, url)
        self.assertFalse(Producto.objects.filter(pk=taladro.pk).exists())
        self.assertEqual(Producto.objects.count(), self.productos_iniciales)
