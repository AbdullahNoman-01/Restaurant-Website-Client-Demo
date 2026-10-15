from django.contrib import admin
from .models import TeamMember, AboutStat, Milestone, Pillar, AboutStory

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'role', 'bio')

@admin.register(AboutStat)
class AboutStatAdmin(admin.ModelAdmin):
    list_display = ('number', 'label', 'order')
    list_editable = ('order',)
    search_fields = ('number', 'label')

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('year', 'title', 'order')
    list_editable = ('order',)
    search_fields = ('year', 'title', 'description')

@admin.register(Pillar)
class PillarAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'description')

@admin.register(AboutStory)
class AboutStoryAdmin(admin.ModelAdmin):
    list_display = ('heading', 'quote_author')
