from django.contrib import admin
from .models import Category, MenuItem, MenuItemGallery

class MenuItemGalleryInline(admin.TabularInline):
    model = MenuItemGallery
    extra = 3
    fields = ('image', 'static_image', 'caption', 'order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)
    search_fields = ('name',)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'badge', 'is_available', 'created_at')
    list_filter = ('category', 'badge', 'is_available')
    search_fields = ('name', 'description')
    list_editable = ('price', 'badge', 'is_available')
    inlines = [MenuItemGalleryInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'price', 'description', 'badge', 'is_available')
        }),
        ('Images', {
            'fields': ('image', 'static_image')
        }),
        ('Feature Highlights (Modal View)', {
            'fields': ('feature_1', 'feature_2', 'feature_3')
        }),
    )


@admin.register(MenuItemGallery)
class MenuItemGalleryAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'caption', 'order')
    list_filter = ('menu_item__category',)
    search_fields = ('menu_item__name', 'caption')
