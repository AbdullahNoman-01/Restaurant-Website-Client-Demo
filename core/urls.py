from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from menu import views as menu_views
from about import views as about_views
from contact import views as contact_views
from reservations import views as reservation_views
from private_dining import views as private_dining_views
from gallery import views as gallery_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('home.urls')),
    path('menu/', include('menu.urls')),
    path('menu/', menu_views.menu_list, name='menu_list'),
    path('menu/', menu_views.menu_list, name='menu'),
    path('about/', include('about.urls')),
    path('about/', about_views.about_view, name='about_view'),
    path('about/', about_views.about_view, name='about'),
    path('contact/', include('contact.urls')),
    path('contact/', contact_views.contact_view, name='contact_view'),
    path('contact/', contact_views.contact_view, name='contact'),
    path('reservations/', include('reservations.urls')),
    path('reservations/', reservation_views.reservations_view, name='reservations_view'),
    path('reservations/', reservation_views.reservations_view, name='reservations'),
    path('private_dining/', include('private_dining.urls')),
    path('private_dining/', private_dining_views.private_dining_view, name='private_dining_view'),
    path('private_dining/', private_dining_views.private_dining_view, name='private_dining'),
    path('gallery/', include('gallery.urls')),
    path('gallery/', gallery_views.gallery_view, name='gallery_view'),
    path('gallery/', gallery_views.gallery_view, name='gallery'),
    path('', views.Base, name='base'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)