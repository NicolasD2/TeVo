from django.urls import path
from tevo import views  # Importa las vistas de la app 'tevo'

urlpatterns = [
    path('', views.login_view, name='home'),  # La raíz mostrará directamente el login
    path('login', views.login_view, name='login'),  # Ruta para el login
    path('registro', views.crear_cuenta_view, name='registro'),  # Ruta para el registro
    path('logout/', views.logout_view, name='logout'), # Ruta para el cierre de sesión
]
