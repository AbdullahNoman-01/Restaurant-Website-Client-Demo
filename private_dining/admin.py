from django.contrib import admin
from .models import PrivateSalon, PrivateMenuPackage, EventService, PrivateEventInquiry

@admin.register(PrivateSalon)
class PrivateSalonAdmin(admin.ModelAdmin):
    list_display = ('name', 'seated_capacity', 'standing_capacity', 'minimum_spend', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'tagline', 'description')

@admin.register(PrivateMenuPackage)
class PrivateMenuPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_person', 'wine_pairing_price', 'badge', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'description')

@admin.register(EventService)
class EventServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_symbol', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'description')

@admin.register(PrivateEventInquiry)
class PrivateEventInquiryAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'full_name', 'company_name', 'event_type', 'preferred_date', 'guest_count', 'preferred_salon', 'status', 'created_at')
    list_filter = ('status', 'event_type', 'preferred_salon', 'preferred_date')
    search_fields = ('reference_id', 'full_name', 'email', 'phone', 'company_name', 'special_requirements')
    list_editable = ('status',)
    readonly_fields = ('reference_id', 'created_at')
    date_hierarchy = 'preferred_date'
    actions = ['mark_in_review', 'mark_proposal_sent', 'mark_confirmed', 'mark_declined']

    def mark_in_review(self, request, queryset):
        queryset.update(status='in_review')
    mark_in_review.short_description = "Mark as Under Review"

    def mark_proposal_sent(self, request, queryset):
        queryset.update(status='proposal_sent')
    mark_proposal_sent.short_description = "Mark as Proposal Transmitted"

    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_confirmed.short_description = "Mark as Confirmed"

    def mark_declined(self, request, queryset):
        queryset.update(status='declined')
    mark_declined.short_description = "Mark as Declined"
