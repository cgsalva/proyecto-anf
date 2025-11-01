# PROYECTO-ANF (Nombre de tu Proyecto)

Este es un proyecto Django para (describe en una oración qué hace tu proyecto).

## 🚀 Configuración Inicial

Este repositorio no incluye la base de datos (`db.sqlite3`) ni el entorno virtual (`venv/`) por diseño, ya que estos archivos son específicos de cada desarrollador.

Para ejecutar el proyecto, sigue estos pasos después de clonar el repositorio:

### 1. Crear el Entorno Virtual

Se recomienda usar un entorno virtual para manejar las dependencias del proyecto.

```bash
# Navega a la carpeta del proyecto
cd proyecto-anf

# Crea un entorno virtual (puedes llamarlo 'venv' como en el .gitignore)
python -m venv venv

#Activar el entorno
source venv/bin/activate

# Correr este comando para crear la base
python manage.py migrate

# Crear un usuario
python manage.py createsuperuser

# Correr el servidor
python manage.py runserver