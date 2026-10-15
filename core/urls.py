from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from menu import views as menu_views
from about import views as about_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('home.urls')),
    path('menu/', include('menu.urls')),
    path('menu/', menu_views.menu_list, name='menu_list'),
    path('about/', include('about.urls')),
    path('about/', about_views.about_view, name='about'),
    path('', views.Base, name='base'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)