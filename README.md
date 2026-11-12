# Catálogo de ferretería (TI3041-ES2)

Aplicación Django para consultar productos de una ferretería, comprar como
consumidor y gestionar productos como administrador.

## Requisitos y ejecución local

Se utiliza SQLite, incluida con Python, por lo que no se necesita instalar
`mysqlclient`. Desde la raíz del proyecto, en Windows:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python catalogo\poblar.py
python manage.py createsuperuser
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` para la portada, `/catalogo/` para el listado y
`/admin/` para la administración de Django. En `/cuenta/registro/` se crean
cuentas de consumidor. El usuario creado con `createsuperuser` puede ingresar
al panel de gestión de la tienda en `/gestionar/`.

El script de poblamiento incorpora 40 productos de ferretería con nombres,
categorías, precios en pesos chilenos y stock inicial. Es repetible: agrega los
productos faltantes, completa las imágenes que estén vacías y no elimina ni
restablece los existentes. Para aplicar esta corrección a una base existente,
ejecuta nuevamente `python catalogo\poblar.py`.

## Base de datos y migraciones

La configuración de desarrollo está en `config/settings.py` y utiliza la base
SQLite local `db.sqlite3`, excluida de Git. Las migraciones que definen los
modelos se encuentran en `catalogo/migrations/`. Para revisar y aplicar
cambios:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Si `/catalogo/` muestra `no such table: catalogo_producto`, ejecuta
`python manage.py migrate` desde la raíz del proyecto y reinicia el servidor.

Si el curso exige una instancia MySQL específica, hay que reemplazar la
configuración SQLite por los datos de conexión entregados por el docente e
instalar el controlador indicado por él. No se incluyen credenciales de base
de datos en este repositorio.

## Pruebas

```powershell
python manage.py check
python manage.py test catalogo
```

## Etapas registradas en Git

El historial contiene los commits `etapa-0-entorno`, `etapa-1-modelo`,
`etapa-2-admin` y `etapa-3-bd`. La entrega de documentación y verificación se
registra en el commit `entrega-final`.

El registro de consultas y asistencia de IA está en [USO_IA.md](USO_IA.md).
