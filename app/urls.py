# app/urls.py
from django.urls import path
from . import views  # <-- ¡ESTA ES LA LÍNEA CORRECTA!

urlpatterns = [
    # Ruta del Dashboard (la página principal de la app)
    path('', views.dashboard, name='dashboard'),
    
    # Ruta para subir los archivos CSV
    path('cargar/', views.upload_data, name='upload_data'),
]