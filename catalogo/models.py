from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    precio = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    imagen = models.URLField(max_length=1000, blank=True)

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


class Coleccion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    productos = models.ManyToManyField(
        Producto,
        blank=True,
        related_name='colecciones',
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=30, blank=True)
    asunto = models.CharField(max_length=120)
    mensaje = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    respondido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.asunto} — {self.nombre}"


class Compra(models.Model):
    consumidor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compras')
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='compras',
    )
    nombre_producto = models.CharField(max_length=100)
    precio_unitario = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField(default=1)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_producto} x {self.cantidad} ({self.consumidor.username})"