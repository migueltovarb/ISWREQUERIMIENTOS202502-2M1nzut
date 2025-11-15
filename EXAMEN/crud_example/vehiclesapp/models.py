from django.db import models

class Vehiculo(models.Model):
    COLORLIST = (
        ('1', 'ROJO'),
        ('2', 'AZUL'),
        ('3', 'VERDE'),
    )
    
    placa = models.CharField(max_length=6)
    marca = models.CharField(max_length=10)
    color = models.CharField('color', max_length=4, choices=COLORLIST)
    modelo = models.IntegerField()
    
    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.placa}"