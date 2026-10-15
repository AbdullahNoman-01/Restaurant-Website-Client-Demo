from django.shortcuts import render
from .models import TeamMember, AboutStat, Milestone

def about_view(request):
    team_members = list(TeamMember.objects.all())
    stats = list(AboutStat.objects.all())
    milestones = list(Milestone.objects.all())

    # Fallback default data if not yet added in admin
    if not team_members:
        team_members = [
            {
                'name': 'Arthur Pendelton',
                'role': 'Executive Head Chef',
                'bio': 'Trained in three-Michelin-starred kitchens across London and Lyon, Arthur brings over 20 years of mastery to modern British gastronomic craft.',
                'get_image_url': '/static/about/media/chef_arthur.jpg',
            },
            {
                'name': 'Eleanor Vance',
                'role': 'Head Sommelier & Cellar Master',
                'bio': 'Curating an exceptional collection of over 300 rare vintages, artisanal biodynamic bottles, and regional English sparkling gems.',
                'get_image_url': '/static/about/media/sommelier_eleanor.jpg',
            },
            {
                'name': 'Marcus Sterling',
                'role': 'Director of Hospitality & GM',
                'bio': 'With two decades presiding over high-society British dining rooms, Marcus ensures every guest experiences effortless poise and genuine warmth.',
                'get_image_url': '/static/about/media/manager_marcus.jpg',
            },
        ]

    if not stats:
        stats = [
            {'number': '15+', 'label': 'Years of Culinary Heritage'},
            {'number': '100%', 'label': 'Locally Foraged & Farm-Sourced'},
            {'number': '250+', 'label': 'Curated Cellar Vintages'},
            {'number': '4.9★', 'label': 'Patron Satisfaction Rating'},
        ]

    if not milestones:
        milestones = [
            {
                'year': '2018',
                'title': 'The Foundation on King Street',
                'description': 'Founded in a restored Victorian banking hall in Manchester with a bold vision: celebrating untamed British terroir through modern technique.'
            },
            {
                'year': '2021',
                'title': 'Farm-to-Fork Direct Alliances',
                'description': 'Established dedicated partnerships with artisan farms in Cumbria, Yorkshire, and coastal Cornwall for pure zero-mile provenance.'
            },
            {
                'year': '2024',
                'title': 'Michelin Guide Distinction',
                'description': 'Awarded prestigious recognition in the Michelin Guide UK for exceptional consistency, theatrical plating, and cellar excellence.'
            },
            {
                'year': '2026',
                'title': 'The Private Vault & Cellar Expansion',
                'description': 'Unveiling our subterranean sommelier vault for bespoke chef tastings, intimate private banquets, and masterclasses.'
            },
        ]

    context = {
        'team_members': team_members,
        'stats': stats,
        'milestones': milestones,
    }
    return render(request, 'about/about.html', context)
