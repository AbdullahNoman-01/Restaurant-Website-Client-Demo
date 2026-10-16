from django.db import models
from django.templatetags.static import static

class HomeHero(models.Model):
    kicker = models.CharField(max_length=150, default="MODERN BRITISH CUISINE")
    headline_line1 = models.CharField(max_length=150, default="Good food.")
    headline_line2 = models.CharField(max_length=150, default="Great times.")
    headline_line3 = models.CharField(max_length=150, default="Made for sharing.")
    description = models.TextField(
        default="Welcome to The Chesterfield, a modern British restaurant in the heart of Manchester. "
                "Seasonal ingredients, expertly crafted dishes, subterranean cellar reserves, and warm Victorian hospitality."
    )
    button_primary_text = models.CharField(max_length=100, default="BOOK A TABLE")
    button_secondary_text = models.CharField(max_length=100, default="VIEW OUR MENU")
    bg_image = models.ImageField(upload_to='home/', blank=True, null=True)
    static_bg_image = models.CharField(max_length=255, default='media/hero-bg.jpg')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Homepage Hero Banner"
        verbose_name_plural = "Homepage Hero Banners"

    def __str__(self):
        return f"Hero Banner: {self.headline_line1} {self.headline_line2}"

    def get_bg_image_url(self):
        if self.bg_image:
            try:
                return self.bg_image.url
            except Exception:
                pass
        return static(self.static_bg_image)


class HomeCriticReview(models.Model):
    critic_name = models.CharField(max_length=150, help_text="e.g. The Times, Michelin Guide, Manchester Evening News")
    reviewer_title = models.CharField(max_length=150, blank=True, default="Restaurant Critic")
    quote = models.TextField(help_text="Critique or testimonial quote")
    rating_stars = models.CharField(max_length=20, default="★★★★★")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Critic Review"
        verbose_name_plural = "Critic Reviews"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.critic_name} ({self.rating_stars})"
