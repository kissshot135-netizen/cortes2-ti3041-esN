from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Coleccion, Contacto, Producto


class RegistroConsumidorForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email']
        if commit:
            usuario.save()
        return usuario


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ('nombre', 'categoria', 'precio', 'stock', 'imagen')
        labels = {
            'nombre': 'Nombre',
            'categoria': 'Categoría',
            'precio': 'Precio',
            'stock': 'Stock inicial',
            'imagen': 'URL de la imagen (opcional)',
        }


class ColeccionForm(forms.ModelForm):
    class Meta:
        model = Coleccion
        fields = ('nombre', 'descripcion', 'productos')
        widgets = {
            'productos': forms.CheckboxSelectMultiple,
        }
        labels = {
            'nombre': 'Nombre de la colección',
            'descripcion': 'Descripción',
            'productos': 'Productos incluidos',
        }


class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ('nombre', 'email', 'telefono', 'asunto', 'mensaje')
        labels = {
            'nombre': 'Nombre',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono (opcional)',
            'asunto': 'Asunto',
            'mensaje': 'Mensaje',
        }
        widgets = {
            'mensaje': forms.Textarea(attrs={'rows': 5}),
        }


class CompraForm(forms.Form):
    cantidad = forms.IntegerField(min_value=1, initial=1, label='Cantidad')
