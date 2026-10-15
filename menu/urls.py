from django.urls import path
from . import views

# app_name = 'menu'

urlpatterns = [
    path('', views.menu_list, name='menu_list'),
    path('details/', views.menu_details, name='menu_details_default'),
    path('details/<int:item_id>/', views.menu_details, name='menu_details'),
]
