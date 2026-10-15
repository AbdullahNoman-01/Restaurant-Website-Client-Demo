from django.shortcuts import render
from .models import TeamMember, AboutStat, Milestone, Pillar, AboutStory

def about_view(request):
    team_members = TeamMember.objects.all()
    stats = AboutStat.objects.all()
    milestones = Milestone.objects.all()
    pillars = Pillar.objects.all()
    story = AboutStory.objects.first()

    context = {
        'team_members': team_members,
        'stats': stats,
        'milestones': milestones,
        'pillars': pillars,
        'story': story,
    }
    return render(request, 'about/about.html', context)
