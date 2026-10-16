from django.db import models
from django.templatetags.static import static

class GalleryCategory(models.Model):
    name = models.CharField(max_length=100, help_text="Display name for filter button")
    slug = models.SlugField(max_length=100, unique=True, help_text="Filter identifier (e.g., gastronomy, interiors)")
    order = models.PositiveIntegerField(default=0, help_text="Display sequence")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Gallery Category"
        verbose_name_plural = "Gallery Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class GalleryItem(models.Model):
    ASPECT_RATIO_CHOICES = (
        ('standard', 'Standard (4:3)'),
        ('landscape', 'Landscape (16:9)'),
        ('portrait', 'Portrait (3:4)'),
        ('tall', 'Tall Panoramic (2:3)'),
        ('wide', 'Wide Feature (2:1)'),
    )

    title = models.CharField(max_length=200, help_text="Title of the photograph")
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='items')
    subtitle = models.CharField(max_length=200, blank=True, help_text="E.g. 'Dry-Aged British Beef' or 'Candlelit Mezzanine'")
    description = models.TextField(blank=True, help_text="Detailed note or narrative about this photograph")
    image = models.ImageField(upload_to='gallery/', blank=True, null=True, help_text="User-uploaded high-res image via Admin")
    static_image = models.CharField(max_length=255, blank=True, default='', help_text="Bundled file name in gallery/static/gallery/media/")
    badge = models.CharField(max_length=60, blank=True, default='', help_text="E.g. 'SIGNATURE DISH', 'RARE VINTAGE', 'PRIVATE SALON'")
    aspect_ratio = models.CharField(max_length=20, choices=ASPECT_RATIO_CHOICES, default='standard')
    photographer_credit = models.CharField(max_length=150, blank=True, default='The Chesterfield Archives')
    featured = models.BooleanField(default=False, help_text="Highlight as a large focal card in the grid")
    order = models.PositiveIntegerField(default=0, help_text="Display sorting order")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Gallery Item"
        verbose_name_plural = "Gallery Items"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.category.name})"

    @property
    def get_image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        if self.static_image:
            return static(f'gallery/media/{self.static_image}')
        return ''


class InstagramHighlight(models.Model):
    title = models.CharField(max_length=150)
    handle = models.CharField(max_length=100, default='@thechesterfield.mcr')
    image = models.ImageField(upload_to='gallery/instagram/', blank=True, null=True)
    static_image = models.CharField(max_length=255, blank=True, default='')
    likes_count = models.CharField(max_length=50, default='1.2k')
    link = models.URLField(default='https://instagram.com')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Instagram Highlight"
        verbose_name_plural = "Instagram Highlights"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.title} - {self.likes_count} likes"

    @property
    def get_image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        if self.static_image:
            return static(f'gallery/media/{self.static_image}')
        return ''


class VirtualTourStat(models.Model):
    stat_number = models.CharField(max_length=50)
    label = models.CharField(max_length=120)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Virtual Tour Stat"
        verbose_name_plural = "Virtual Tour Stats"
        ordering = ['order']

    def __str__(self):
        return f"{self.stat_number} {self.label}"
