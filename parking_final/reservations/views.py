from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import ParkingLot, Reservation, Payment
from .forms import CustomUserCreationForm, ReservationForm, PaymentForm
from django.utils import timezone  # ← AGREGAR ESTA IMPORTACIÓN

def home(request):
    return render(request, 'reservations/home.html')

@login_required
def parking_list(request):
    parking_lots = ParkingLot.objects.filter(is_active=True)
    return render(request, 'reservations/parking_list.html', {
        'parking_lots': parking_lots
    })

@login_required
def create_reservation(request, parking_lot_id):

    print(f"DEBUG: Método: {request.method}")  # ← Agregar esto
    print(f"DEBUG: POST data: {request.POST}")  # ← Agregar esto
    
    parking_lot = get_object_or_404(ParkingLot, id=parking_lot_id, is_active=True)
    
    if parking_lot.available_spaces() <= 0:
        messages.error(request, "No hay espacios disponibles en este parqueadero.")
        return redirect('parking_list')
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            try:
                reservation = form.save(commit=False)
                reservation.user = request.user
                reservation.parking_lot = parking_lot
                
                # Las fechas ya deberían estar validadas en el form
                reservation.save()
                
                messages.success(request, "Reserva creada exitosamente. Proceda al pago.")
                return redirect('payment', reservation_id=reservation.id)
                
            except Exception as e:
                messages.error(request, f"Error al crear la reserva: {str(e)}")
        else:
            # Mostrar errores específicos del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
    else:
        # Formulario inicial - establecer el parking_lot por defecto
        form = ReservationForm(initial={'parking_lot': parking_lot})
    
    return render(request, 'reservations/reservation.html', {
        'form': form,
        'parking_lot': parking_lot
    })

@login_required
def payment_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    if reservation.status != 'pending':
        messages.error(request, "Esta reserva ya ha sido procesada.")
        return redirect('parking_list')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            
            payment = Payment.objects.create(
                reservation=reservation,
                amount=reservation.total_amount,
                payment_method=payment_method,
                transaction_id=f"TXN{timezone.now().strftime('%Y%m%d%H%M%S')}",  # ← USAR timezone.now()
                status='completed'
            )
            
            reservation.payment_method = payment_method
            reservation.status = 'confirmed'
            reservation.save()
            
            messages.success(request, "Pago exitoso!")
            return redirect('qr_code', reservation_id=reservation.id)
    else:
        form = PaymentForm()
    
    return render(request, 'reservations/payment.html', {
        'form': form,
        'reservation': reservation
    })

@login_required
def qr_code_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    qr_code_url = reservation.get_qr_code_url()
    
    return render(request, 'reservations/qr_code.html', {
        'reservation': reservation,
        'qr_code_url': qr_code_url
    })

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registro exitoso!")
            return redirect('parking_list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'reservations/register.html', {'form': form})

@login_required
def user_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'reservations/user_reservations.html', {'reservations': reservations})

@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    if reservation.status in ['pending', 'confirmed']:
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, "Reserva cancelada.")
    else:
        messages.error(request, "No se puede cancelar esta reserva.")
    
    return redirect('user_reservations')