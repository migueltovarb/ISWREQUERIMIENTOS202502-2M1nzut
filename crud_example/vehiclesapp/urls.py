from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='home'),          
    path('vehiculos/', views.lista_vehiculos, name='lista_vehiculos'),
    path('crear/', views.crear_vehiculo, name='crear_vehiculo'),
    path('editar/<int:id>/', views.editar_vehiculo, name='editar_vehiculo'),
    path('eliminar/<int:id>/', views.eliminar_vehiculo, name='eliminar_vehiculo'),
]