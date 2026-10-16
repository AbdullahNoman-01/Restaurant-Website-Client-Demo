from django.shortcuts import render
from .models import GalleryCategory, GalleryItem, InstagramHighlight, VirtualTourStat

def gallery_view(request):
    categories = GalleryCategory.objects.filter(is_active=True).order_by('order')
    items = GalleryItem.objects.filter(is_active=True).select_related('category').order_by('order', '-created_at')
    instagram_posts = InstagramHighlight.objects.filter(is_active=True).order_by('order')
    stats = VirtualTourStat.objects.filter(is_active=True).order_by('order')

    context = {
        'categories': categories,
        'items': items,
        'instagram_posts': instagram_posts,
        'stats': stats,
    }
    return render(request, 'gallery/gallery.html', context)
