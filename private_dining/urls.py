from django.urls import path
from . import views

app_name = 'private_dining'

urlpatterns = [
    path('', views.private_dining_view, name='private_dining_view'),
    path('index/', views.private_dining_view, name='private_dining'),
]
