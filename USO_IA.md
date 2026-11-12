# Registro de uso de inteligencia artificial

Este registro resume las consultas realizadas durante el desarrollo y la forma
en que se utilizaron las respuestas. Los cambios se revisaron y probaron en el
proyecto; la IA no reemplazó la ejecución de migraciones, pruebas ni la revisión
del repositorio.

| Fecha | Consulta o propósito | Uso en el proyecto | Revisión realizada |
|---|---|---|---|
| 2026-10-05 | Solicitud para solucionar los errores del proyecto Django y del archivo de vistas del catálogo. | Se revisaron la inscripción de la aplicación, la ruta del template y las migraciones necesarias para el modelo `Producto`. | Se ejecutaron `manage.py check` y una solicitud de prueba al inicio del sitio. |
| 2026-10-05 | Solicitud de una portada con acceso al catálogo y compra, inicio de sesión para consumidores y administradores y gestión de productos. | Se implementaron formularios, vistas, rutas y plantillas para registro, ingreso, compra con descuento de stock, creación y eliminación administrativa. | Se añadieron y ejecutaron pruebas para registro, redirecciones según rol, control de stock y restricciones de administrador. |
| 2026-10-05 | Solicitud para adecuar el trabajo a las etapas 0–3 y a la entrega final de la evaluación. | Se revisaron los commits existentes; se documentaron ejecución, base de datos y migraciones; se hizo no destructivo el script de carga de productos y se registró esta asistencia. | Se verificaron los datos cargados, las migraciones, los checks de Django y la suite de pruebas. |

## Contenido de datos asistido por IA

`catalogo/poblar.py` contiene 40 productos ficticios y realistas en español
para una ferretería, con categorías, precios de referencia en pesos chilenos y
stock inicial. Son datos de demostración, no corresponden a inventario ni
precios de un proveedor real. El script usa el ORM de Django y conserva los
productos que ya existan.

## Límites y decisiones

- Las cuentas de consumidor se registran desde el sitio. La administración se
  concede por separado mediante `createsuperuser` o desde el panel de Django;
  el formulario público nunca crea cuentas con permisos administrativos.
- Se mantuvo SQLite, que es la base configurada en el repositorio y permite
  ejecutar el proyecto sin un servicio externo. Si la pauta del curso exige
  valores concretos para MySQL, deben configurarse con los datos del docente y
  no guardarse credenciales en el control de versiones.
- No se registraron contraseñas, claves ni credenciales en este documento.
