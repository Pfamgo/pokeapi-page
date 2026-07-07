# Despliegue en Render

## Opción 1: Usando render.yaml (recomendado)

El repositorio incluye un archivo `render.yaml` con toda la configuración.

1. En Render, ve a **Dashboard > New > Blueprint**
2. Conecta el repositorio
3. Render detectará automáticamente el `render.yaml` y configurará el servicio

## Opción 2: Web Service manual

1. **Crear Web Service**
   - Conectar repositorio de GitHub
   - Elegir **Web Service**
   - Nombre: `pokeview`

2. **Configurar el servicio**
   - **Runtime:** Python 3
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py import_pokemon
     ```
   - **Start Command:**
     ```bash
     gunicorn pokeview.wsgi:application --workers=4 --worker-class=sync --timeout=120
     ```
   - **Plan:** Free (o Starter para mejor rendimiento)

3. **Variables de Entorno**
   | Variable | Valor |
   |---|---|
   | `DJANGO_SECRET_KEY` | (generado automáticamente) |
   | `DJANGO_DEBUG` | `False` |
   | `DJANGO_ALLOWED_HOSTS` | `.onrender.com,localhost,127.0.0.1` |
   | `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://*.onrender.com` |
   | `PYTHON_VERSION` | `3.12.1` |

## Persistencia de SQLite

Render usa discos efímeros. Los datos se pierden al reiniciar el servicio.
Para persistencia real, migrar a PostgreSQL.
