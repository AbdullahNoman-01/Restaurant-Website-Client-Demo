from django.shortcuts import render, get_object_or_404
from .models import Category, MenuItem, MenuItemGallery

def menu_list(request):
    categories = Category.objects.all().order_by('order')
    menu_items = MenuItem.objects.filter(is_available=True).select_related('category').prefetch_related('gallery_images')
    
    return render(request, 'menu/menu.html', {
        'categories': categories,
        'menu_items': menu_items,
    })


def menu_details(request, item_id=None):
    if item_id:
        item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    else:
        item = MenuItem.objects.filter(is_available=True).first()
        if not item:
            # Fallback if database is empty
            item = MenuItem.objects.first()

    related_items = []
    if item:
        related_items = MenuItem.objects.filter(
            category=item.category,
            is_available=True
        ).exclude(id=item.id)[:4]

    return render(request, 'menu/menu_details.html', {
        'item': item,
        'related_items': related_items,
    })
