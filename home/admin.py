from django.contrib import admin
from .models import HomeHero, HomeCriticReview

@admin.register(HomeHero)
class HomeHeroAdmin(admin.ModelAdmin):
    list_display = ('kicker', 'headline_line1', 'headline_line2', 'is_active')
    list_editable = ('is_active',)


@admin.register(HomeCriticReview)
class HomeCriticReviewAdmin(admin.ModelAdmin):
    list_display = ('critic_name', 'reviewer_title', 'rating_stars', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('critic_name', 'quote')
