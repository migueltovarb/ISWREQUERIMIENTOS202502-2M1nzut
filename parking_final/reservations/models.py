from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal  # ← AGREGAR ESTA IMPORTACIÓN
import secrets
import json
import urllib.parse

class ParkingLot(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    total_spaces = models.IntegerField()
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    def available_spaces(self):
        try:
            now = timezone.now()
            reserved_count = Reservation.objects.filter(
                parking_lot=self,
                start_time__lte=now,
                end_time__gte=now,
                status__in=['confirmed', 'active']
            ).count()
            return max(0, self.total_spaces - reserved_count)
        except:
            return self.total_spaces
    
    def __str__(self):
        return self.name

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('active', 'Activa'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]
    
    PAYMENT_METHODS = [
        ('credit_card', 'Tarjeta de Crédito'),
        ('debit_card', 'Tarjeta de Débito'),
        ('digital_wallet', 'Billetera Digital'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    license_plate = models.CharField(max_length=10)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    qr_code_data = models.TextField(blank=True)
    access_code = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_total(self):
        duration = self.end_time - self.start_time
        hours = duration.total_seconds() / 3600
        
        # Convertir a Decimal y luego multiplicar
        hours_decimal = Decimal(str(hours))  # ← CONVERTIR A DECIMAL
        return hours_decimal * self.parking_lot.hourly_rate
    
    def generate_access_code(self):
        if not self.access_code:
            self.access_code = secrets.token_urlsafe(32)
    
    def generate_qr_data(self):
        if not self.access_code:
            self.generate_access_code()
        
        qr_data = {
            'system': 'ParkingSystem',
            'reservation_id': self.id,
            'access_code': self.access_code,
            'license_plate': self.license_plate,
        }
        self.qr_code_data = json.dumps(qr_data)
    
    def get_qr_code_url(self):
        if not self.qr_code_data:
            self.generate_qr_data()
            self.save()
        
        simple_data = f"PARKING|{self.id}|{self.access_code}|{self.license_plate}"
        encoded_data = urllib.parse.quote(simple_data)
        return f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_data}"
    
    def save(self, *args, **kwargs):
        if not self.access_code:
            self.generate_access_code()
        
        if not self.total_amount:
            self.total_amount = self.calculate_total()
        
        if not self.qr_code_data:
            self.generate_qr_data()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Reserva {self.id} - {self.user.username}"

class Payment(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=Reservation.PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Pago {self.transaction_id}"