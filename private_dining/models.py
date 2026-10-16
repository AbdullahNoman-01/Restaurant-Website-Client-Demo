import uuid
from django.db import models

class PrivateSalon(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=100, unique=True)
    tagline = models.CharField(max_length=200)
    description = models.TextField()
    seated_capacity = models.CharField(max_length=100, default="Up to 18 Guests Seated")
    standing_capacity = models.CharField(max_length=100, default="Up to 30 Guests Reception")
    minimum_spend = models.CharField(max_length=150, default="Lunch from £1,200 • Dinner from £2,500")
    key_features = models.CharField(max_length=255, default="Dedicated sommelier, acoustic privacy, custom florals")
    image = models.ImageField(upload_to='salons/', blank=True, null=True)
    static_image = models.CharField(max_length=255, default='private_dining/media/salon_vault.jpg')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name_plural = "Private Dining Salons & Spaces"

    def __str__(self):
        return f"{self.name} ({self.seated_capacity})"

    def get_image_url(self):
        if self.image:
            return self.image.url
        return f"/static/{self.static_image}"


class PrivateMenuPackage(models.Model):
    name = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=200, default="Curated Seasonal Feasting")
    price_per_person = models.CharField(max_length=100, default="£85 per guest")
    wine_pairing_price = models.CharField(max_length=100, default="Sommelier Flight: +£55")
    description = models.TextField()
    course_1 = models.CharField(max_length=200, blank=True)
    course_2 = models.CharField(max_length=200, blank=True)
    course_3 = models.CharField(max_length=200, blank=True)
    course_4 = models.CharField(max_length=200, blank=True)
    badge = models.CharField(max_length=50, blank=True, default="POPULAR")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name_plural = "Private Feasting & Tasting Menus"

    def __str__(self):
        return f"{self.name} - {self.price_per_person}"


class EventService(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    icon_symbol = models.CharField(max_length=10, default="✦")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name_plural = "Event Amenities & Inclusions"

    def __str__(self):
        return self.title


class PrivateEventInquiry(models.Model):
    EVENT_TYPE_CHOICES = [
        ('private_dinner', 'Private Celebration Dinner / Supper Club'),
        ('corporate', 'Corporate Banquet & Executive Entertaining'),
        ('anniversary', 'Milestone Anniversary or Birthday Gathering'),
        ('wedding', 'Intimate Wedding Banquet or Rehearsal Dinner'),
        ('tasting', 'Sommelier Cellar Masterclass & Tasting'),
        ('buyout', 'Full Restaurant Takeover (Exclusive Hire)'),
    ]

    TIME_SLOT_CHOICES = [
        ('lunch', 'Lunch Service (12:00 PM – 4:00 PM)'),
        ('dinner', 'Evening Dinner (6:00 PM – 11:30 PM)'),
        ('full_day', 'All-Day Exclusive Access'),
    ]

    STATUS_CHOICES = [
        ('new', 'New Inquiry'),
        ('in_review', 'Under Maître D\' Review'),
        ('proposal_sent', 'Proposal Transmitted'),
        ('confirmed', 'Deposit Received & Confirmed'),
        ('declined', 'Declined / Withdrawn'),
    ]

    reference_id = models.CharField(max_length=30, unique=True, editable=False)
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    company_name = models.CharField(max_length=150, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, default='private_dinner')
    preferred_salon = models.ForeignKey(PrivateSalon, on_delete=models.SET_NULL, null=True, blank=True)
    preferred_date = models.DateField()
    preferred_time_slot = models.CharField(max_length=30, choices=TIME_SLOT_CHOICES, default='dinner')
    guest_count = models.PositiveIntegerField(default=12)
    estimated_budget = models.CharField(max_length=100, blank=True, help_text="e.g. £2,000 – £5,000")
    special_requirements = models.TextField(blank=True, help_text="Dietary needs, AV presentation, bespoke florals, sommelier flight")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Private Dining Inquiries"

    def __str__(self):
        return f"{self.reference_id} - {self.full_name} ({self.guest_count} Guests on {self.preferred_date})"

    def save(self, *args, **kwargs):
        if not self.reference_id:
            self.reference_id = f"PD-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
