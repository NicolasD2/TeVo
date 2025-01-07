from django.urls import path
from . import views

urlpatterns = [
    path('crear_encuesta/', views.crear_encuesta, name='crear_encuesta'),
    path('ver_resultados_encuesta/', views.ver_resultados_encuesta, name='ver_resultados_encuesta'),
    # otras rutas...
]