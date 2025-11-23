from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),  # ← ESTA ES LA PÁGINA PRINCIPAL
    path('parking/', views.parking_list, name='parking_list'),
    path('reserve/<int:parking_lot_id>/', views.create_reservation, name='create_reservation'),
    path('payment/<int:reservation_id>/', views.payment_view, name='payment'),
    path('qr-code/<int:reservation_id>/', views.qr_code_view, name='qr_code'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='reservations/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('my-reservations/', views.user_reservations, name='user_reservations'),
    path('cancel-reservation/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
]