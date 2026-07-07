# Despliegue en Render

## Requisitos

- Cuenta en [Render](https://render.com)
- Repositorio conectado a Render

## Pasos

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
   - `PYTHON_VERSION`: `3.12.1`
   - `DJANGO_SETTINGS_MODULE`: `pokeview.settings`
   - `DISABLE_COLLECTSTATIC`: `1` (si se maneja manualmente)

4. **Persistencia de SQLite**
   Render usa discos efímeros. Para persistencia en Free tier:
   - Los datos se mantienen mientras el servicio no se reinicie
   - Para persistencia real, migrar a **PostgreSQL** (recomendado para producción)
   - Alternativa: Usar [Render Disks](https://render.com/docs/disks) (solo planes pagos)

## Archivos importantes

- `requirements.txt` - Dependencias del proyecto
- `Procfile` (opcional) - Alternativa al Start Command
- `runtime.txt` (opcional) - Especificar versión de Python

## Procfile (alternativa)

```
web: gunicorn pokeview.wsgi:application --workers=4 --timeout=120
```
