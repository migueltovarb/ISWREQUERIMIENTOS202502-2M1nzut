from django.shortcuts import render, redirect
from .forms import VehiculoForm
from .models import Vehiculo  # ← Agregar esta línea

def inicio(request):
    return render(request, 'inicio.html')

def lista_vehiculos(request):
    vehiculos = Vehiculo.objects.all()  # ← Obtener todos los vehículos
    return render(request, 'lista_vehiculos.html', {'vehiculos': vehiculos})

def crear_vehiculo(request):
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_vehiculos')
    else:
        form = VehiculoForm()
    
    return render(request, 'crear_vehiculo.html', {'form': form})

def editar_vehiculo(request, id):
    vehiculo = Vehiculo.objects.get(id=id)
    if request.method == 'POST':
        form = VehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()
            return redirect('lista_vehiculos')
    else:
        form = VehiculoForm(instance=vehiculo)
    
    return render(request, 'editar_vehiculo.html', {'form': form})

def eliminar_vehiculo(request, id):
    vehiculo = Vehiculo.objects.get(id=id)
    if request.method == 'POST':
        vehiculo.delete()
        return redirect('lista_vehiculos')
    return render(request, 'eliminar_vehiculo.html', {'vehiculo': vehiculo})