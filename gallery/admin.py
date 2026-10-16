from django.contrib import admin
from .models import GalleryCategory, GalleryItem, InstagramHighlight, VirtualTourStat

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'badge', 'aspect_ratio', 'featured', 'order', 'is_active')
    list_filter = ('category', 'badge', 'aspect_ratio', 'featured', 'is_active')
    list_editable = ('order', 'featured', 'is_active')
    search_fields = ('title', 'subtitle', 'description', 'photographer_credit')
    fieldsets = (
        ('Photo Overview', {
            'fields': ('title', 'subtitle', 'category', 'badge', 'featured')
        }),
        ('Image Assets', {
            'fields': ('image', 'static_image', 'aspect_ratio', 'photographer_credit')
        }),
        ('Narrative & Narrative', {
            'fields': ('description',)
        }),
        ('Ordering & Status', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(InstagramHighlight)
class InstagramHighlightAdmin(admin.ModelAdmin):
    list_display = ('title', 'handle', 'likes_count', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'handle')


@admin.register(VirtualTourStat)
class VirtualTourStatAdmin(admin.ModelAdmin):
    list_display = ('stat_number', 'label', 'order', 'is_active')
    list_editable = ('order', 'is_active')
