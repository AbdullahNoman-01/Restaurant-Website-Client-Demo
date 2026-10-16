from django.contrib import admin
from .models import SeatingArea, DiningExperience, ReservationPolicy, TableReservation

@admin.register(SeatingArea)
class SeatingAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'minimum_spend', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'tagline', 'description')

@admin.register(DiningExperience)
class DiningExperienceAdmin(admin.ModelAdmin):
    list_display = ('name', 'timing', 'price_hint', 'badge', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'description')

@admin.register(ReservationPolicy)
class ReservationPolicyAdmin(admin.ModelAdmin):
    list_display = ('title', 'lead_time_info')

@admin.register(TableReservation)
class TableReservationAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'guest_name', 'guests_count', 'reservation_date', 'reservation_time', 'seating_area', 'status', 'created_at')
    list_filter = ('status', 'reservation_date', 'seating_area', 'occasion')
    search_fields = ('booking_reference', 'guest_name', 'guest_email', 'guest_phone', 'special_requests')
    list_editable = ('status',)
    readonly_fields = ('booking_reference', 'created_at')
    date_hierarchy = 'reservation_date'
    actions = ['mark_as_confirmed', 'mark_as_seated', 'mark_as_completed', 'mark_as_cancelled']

    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_as_confirmed.short_description = "Mark selected as Confirmed"

    def mark_as_seated(self, request, queryset):
        queryset.update(status='seated')
    mark_as_seated.short_description = "Mark selected as Seated"

    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected as Completed"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "Mark selected as Cancelled"
