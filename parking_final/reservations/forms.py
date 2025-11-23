from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Reservation
from django.utils import timezone

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['parking_lot', 'license_plate', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if timezone.is_naive(start_time):
                start_time = timezone.make_aware(start_time)
                cleaned_data['start_time'] = start_time
            if timezone.is_naive(end_time):
                end_time = timezone.make_aware(end_time)
                cleaned_data['end_time'] = end_time
            
            if start_time >= end_time:
                raise forms.ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
            
            if start_time < timezone.now():
                raise forms.ValidationError("No se puede reservar en el pasado.")
        
        return cleaned_data

class PaymentForm(forms.Form):
    PAYMENT_METHODS = [
        ('credit_card', 'Tarjeta de Crédito'),
        ('debit_card', 'Tarjeta de Débito'),
        ('digital_wallet', 'Billetera Digital'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS, 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True,
        label="Método de Pago"
    )
    
    # Campos para tarjeta de crédito/débito
    card_number = forms.CharField(
        max_length=16,
        required=False,
        label="Número de Tarjeta",
        widget=forms.TextInput(attrs={'placeholder': '1234 5678 9012 3456'})
    )
    
    card_holder = forms.CharField(
        max_length=100,
        required=False,
        label="Nombre en la Tarjeta",
        widget=forms.TextInput(attrs={'placeholder': 'JUAN PEREZ'})
    )
    
    expiry_date = forms.CharField(
        max_length=5,
        required=False,
        label="Fecha de Expiración (MM/AA)",
        widget=forms.TextInput(attrs={'placeholder': '12/25'})
    )
    
    cvv = forms.CharField(
        max_length=3,
        required=False,
        label="CVV",
        widget=forms.TextInput(attrs={'placeholder': '123'})
    )
    
    # Campo para billetera digital
    wallet_token = forms.CharField(
        max_length=100,
        required=False,
        label="Token de Billetera",
        widget=forms.TextInput(attrs={'placeholder': 'Ingresa tu token'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method in ['credit_card', 'debit_card']:
            if not cleaned_data.get('card_number'):
                raise forms.ValidationError("El número de tarjeta es requerido para pagos con tarjeta.")
            if not cleaned_data.get('card_holder'):
                raise forms.ValidationError("El nombre en la tarjeta es requerido.")
            if not cleaned_data.get('expiry_date'):
                raise forms.ValidationError("La fecha de expiración es requerida.")
            if not cleaned_data.get('cvv'):
                raise forms.ValidationError("El CVV es requerido.")
            
            # Validar formato de número de tarjeta (solo dígitos)
            card_number = cleaned_data.get('card_number', '').replace(' ', '')
            if not card_number.isdigit() or len(card_number) not in [15, 16]:
                raise forms.ValidationError("El número de tarjeta debe tener 15 o 16 dígitos.")
                
        elif payment_method == 'digital_wallet':
            if not cleaned_data.get('wallet_token'):
                raise forms.ValidationError("El token de billetera digital es requerido.")
        
        return cleaned_data