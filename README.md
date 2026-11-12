# Catálogo Online (TI3041 ES3 + API ES4)

Aplicación Django para que una ferretería administre productos y colecciones,
consulte reportes del negocio, reciba mensajes de clientes y publique una API
JSON para integraciones. Incluye carrito de compras persistido en la sesión.

## Requisitos y ejecución local

Se utiliza SQLite, incluida con Python. Desde PowerShell en la raíz:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python catalogo\poblar.py
python manage.py createsuperuser
python manage.py runserver
```

La clave Django se genera al iniciar si no existe `DJANGO_SECRET_KEY` en el
entorno. Para un entorno desplegado define una clave persistente, configura
`DJANGO_ALLOWED_HOSTS` y deja `DJANGO_DEBUG=false`.

El poblamiento agrega los 40 productos de demostración y completa las imágenes
vacías de productos existentes sin reemplazar valores personalizados.

## Funcionalidades web

- Catálogo público y CRUD de productos para administradores en `/gestionar/`.
- Colecciones de productos en `/colecciones/`; su CRUD está en
  `/gestionar/colecciones/`.
- Dos reportes privados para administradores en `/gestionar/reportes/`:
  inventario agrupado por categoría y productos más vendidos/ingresos. Ambos
  cálculos usan agregaciones del ORM.
- Formulario público de contacto en `/contacto/`; los mensajes quedan guardados
  y se revisan desde el panel de administración de Django.
- Carrito de sesión accesible en `/carrito/`. Se puede armar sin iniciar sesión;
  para confirmar la compra se requiere una cuenta de consumidor.
- Registro de consumidores en `/cuenta/registro/`. Las cuentas administrativas
  se crean con `createsuperuser`; el registro público no concede esos permisos.

## API JSON

Base: `/api/v1/`. Las lecturas de productos y colecciones son públicas. Para
crear, editar o eliminar esos recursos se requiere una sesión autenticada de
administrador y protección CSRF. El envío de contactos es público; su listado
es administrativo.

| Ruta | Métodos | Uso |
|---|---|---|
| `/api/v1/` | GET | Índice de recursos |
| `/api/v1/productos/` | GET, POST | Listar y crear productos |
| `/api/v1/productos/{id}/` | GET, PUT, PATCH, DELETE | Consultar y administrar un producto |
| `/api/v1/colecciones/` | GET, POST | Listar y crear colecciones |
| `/api/v1/colecciones/{id}/` | GET, PUT, PATCH, DELETE | Consultar y administrar una colección |
| `/api/v1/contactos/` | POST, GET | Crear un mensaje; listado solo para administradores |

Las respuestas y errores usan JSON. Por ejemplo:

```powershell
curl.exe http://127.0.0.1:8000/api/v1/productos/
```

Las solicitudes de escritura usan JSON y respetan permisos y CSRF de Django.

## Base de datos y pruebas

La base local `db.sqlite3` está excluida de Git. Para aplicar cambios de
modelos:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Ejecuta los controles y pruebas:

```powershell
python manage.py check
python manage.py test catalogo
```

## Trazabilidad de etapas y uso de IA

El trabajo se organiza en cuatro commits: modelos y formularios, funcionalidades
web, carrito de sesión y API/documentación. El registro de consultas y revisión
está en [uso_ia.md](uso_ia.md).
