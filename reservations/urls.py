from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.reservations_view, name='reservations_view'),
    path('index/', views.reservations_view, name='reservations'),
]
