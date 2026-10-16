from django.shortcuts import render
from .models import HomeHero, HomeCriticReview
from about.models import AboutStory, AboutStat, Pillar
from menu.models import Category, MenuItem
from reservations.models import SeatingArea, DiningExperience
from private_dining.models import PrivateSalon, PrivateMenuPackage
from gallery.models import GalleryItem
from contact.models import ContactInfo, ContactDepartment

def home_view(request):
    hero = HomeHero.objects.filter(is_active=True).first()
    critic_reviews = HomeCriticReview.objects.filter(is_active=True)
    
    # 1. About Preview
    about_story = AboutStory.objects.first()
    about_stats = AboutStat.objects.all()[:4]
    pillars = Pillar.objects.all()[:3]

    # 2. Menu Preview (Curated Signature Dishes)
    menu_categories = Category.objects.all()[:5]
    featured_dishes = MenuItem.objects.filter(is_available=True)[:6]

    # 3. Reservations Preview (Atmospheric Seating Zones)
    seating_areas = SeatingArea.objects.filter(is_active=True)[:4]
    dining_experiences = DiningExperience.objects.all()[:3]

    # 4. Private Dining Preview (Grand Salons & Packages)
    private_salons = PrivateSalon.objects.filter(is_active=True)[:3]
    private_menus = PrivateMenuPackage.objects.all()[:2]

    # 5. Gallery Preview (Photographic Chronicle)
    gallery_preview_items = GalleryItem.objects.filter(is_active=True)[:6]

    # 6. Contact / Location Preview
    contact_info = ContactInfo.objects.first()
    departments = ContactDepartment.objects.all()[:3]

    context = {
        'hero': hero,
        'critic_reviews': critic_reviews,
        'about_story': about_story,
        'about_stats': about_stats,
        'pillars': pillars,
        'menu_categories': menu_categories,
        'featured_dishes': featured_dishes,
        'seating_areas': seating_areas,
        'dining_experiences': dining_experiences,
        'private_salons': private_salons,
        'private_menus': private_menus,
        'gallery_preview_items': gallery_preview_items,
        'contact_info': contact_info,
        'departments': departments,
    }
    return render(request, 'home/home.html', context)
