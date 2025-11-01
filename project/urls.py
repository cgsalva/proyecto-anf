# project/urls.py
from django.contrib import admin
from django.urls import path, include  # <-- ¡Asegúrate de incluir 'include'!
from django.contrib.auth import views as auth_views # Para el login

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Rutas de Login y Logout (integradas)
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html'
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
    ), name='logout'),

    # 2. Rutas de tu aplicación (dashboard, cargar)
    path('', include('app.urls')),
]