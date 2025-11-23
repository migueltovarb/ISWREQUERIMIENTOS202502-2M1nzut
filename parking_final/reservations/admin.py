from django.contrib import admin
from .models import ParkingLot, Reservation, Payment

@admin.register(ParkingLot)
class ParkingLotAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'total_spaces', 'hourly_rate', 'is_active']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'parking_lot', 'license_plate', 'start_time', 'status']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'reservation', 'amount', 'status']