from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, help_text="URL slug used for category tab filtering")
    order = models.PositiveIntegerField(default=0, help_text="Display order in tabs")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    BADGE_CHOICES = [
        ('', 'No Badge'),
        ('Popular', 'Popular'),
        ('New', 'New'),
        ("Chef's Special", "Chef's Special"),
        ('Premium', 'Premium'),
        ('Signature', 'Signature'),
        ('Seasonal', 'Seasonal'),
        ('Cellar Selection', 'Cellar Selection'),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text="Price in USD (e.g. 28.00)")
    description = models.TextField(help_text="Detailed description of the dish")
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True, help_text="Upload dish image from admin")
    static_image = models.CharField(max_length=255, blank=True, null=True, help_text="Internal static path fallback (e.g. menu/media/ribeye_steak.jpg)")
    badge = models.CharField(max_length=50, choices=BADGE_CHOICES, blank=True, default='', help_text="Optional highlight badge")
    
    # Feature bullet points (Image 2)
    feature_1 = models.CharField(max_length=200, default="Fresh & Premium Ingredients")
    feature_2 = models.CharField(max_length=200, default="Chef's Special")
    feature_3 = models.CharField(max_length=200, default="Served with Seasonal Vegetables & House Sauce")
    
    is_available = models.BooleanField(default=True, help_text="Uncheck to temporarily hide from menu")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'id']

    def __str__(self):
        return f"{self.name} (${self.price})"

    @property
    def formatted_price(self):
        return f"${self.price:.2f}"

    def get_image_url(self):
        if self.image:
            return self.image.url
        if self.static_image:
            return f"/static/{self.static_image}"
        return "/static/menu/media/ribeye_steak.jpg"


class MenuItemGallery(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='menu_gallery/', blank=True, null=True)
    static_image = models.CharField(max_length=255, blank=True, null=True)
    caption = models.CharField(max_length=150, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Menu Item Gallery Images"
        ordering = ['order', 'id']

    def __str__(self):
        return f"Gallery for {self.menu_item.name} #{self.order}"

    def get_image_url(self):
        if self.image:
            return self.image.url
        if self.static_image:
            return f"/static/{self.static_image}"
        return self.menu_item.get_image_url()
