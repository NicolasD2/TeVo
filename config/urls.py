from django.urls import path
from tevo import views  # Importa las vistas de la app 'tevo'

urlpatterns = [
    path('', views.login_view, name='home'),
    path('login', views.login_view, name='login'),
    path('registro', views.crear_cuenta_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('health/', views.health, name='health_check'),
    path('ver_encuestas/', views.ver_encuestas, name='ver_encuestas'),
    path('votos/', views.votos, name='votos'),  
    path('ver_resultados_encuesta/', views.ver_resultados_encuesta, name= 'ver_resultados_encuesta'),
    path('crear_encuesta/', views.crear_encuesta, name ='crear_encuesta'),
]