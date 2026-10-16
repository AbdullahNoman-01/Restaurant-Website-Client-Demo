import uuid
from django.db import models

class SeatingArea(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=100, unique=True)
    tagline = models.CharField(max_length=200)
    description = models.TextField()
    capacity = models.CharField(max_length=100, default="1 to 8 Guests")
    minimum_spend = models.CharField(max_length=100, default="Standard A La Carte")
    image = models.ImageField(upload_to='seating_areas/', blank=True, null=True)
    static_image = models.CharField(max_length=255, default='reservations/media/area_grand_hall.jpg')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name_plural = "Seating Areas & Salons"

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image:
            return self.image.url
        return f"/static/{self.static_image}"


class DiningExperience(models.Model):
    name = models.CharField(max_length=150)
    timing = models.CharField(max_length=150)
    price_hint = models.CharField(max_length=150)
    description = models.TextField()
    badge = models.CharField(max_length=50, blank=True, default="POPULAR")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name_plural = "Dining Experiences & Menus"

    def __str__(self):
        return f"{self.name} ({self.price_hint})"


class ReservationPolicy(models.Model):
    title = models.CharField(max_length=200, default="Dining & Reservation Policies")
    lead_time_info = models.CharField(max_length=255, default="Reservations open 60 days in advance at 9:00 AM daily.")
    cancellation_policy = models.TextField(default="We request 24 hours notice for any cancellations or party size reductions. For the Chef's Table and Private Vault, 48 hours notice is required.")
    table_holding_time = models.CharField(max_length=200, default="Tables are held for 15 minutes past the reserved seating time before release.")
    large_party_info = models.TextField(default="For parties of 8 or more, we serve our Seasonal Feasting Menu to ensure seamless service.")
    dress_code = models.CharField(max_length=200, default="Smart Casual • Sophisticated evening attire recommended • No sportswear after 6 PM.")
    corkage_policy = models.CharField(max_length=200, default="£35 per 750ml bottle (maximum 2 bottles per party, excludes wines already on our cellar list).")

    class Meta:
        verbose_name_plural = "Reservation Policy & Protocols"

    def __str__(self):
        return self.title


class TableReservation(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('seated', 'Seated'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    OCCASION_CHOICES = [
        ('casual', 'Casual Dining / Friendly Catch-up'),
        ('date_night', 'Romantic Date Night'),
        ('anniversary', 'Anniversary Celebration'),
        ('birthday', 'Birthday Gathering'),
        ('business', 'Business Dinner / Corporate Hospitality'),
        ('special', 'Landmark Celebration'),
    ]

    booking_reference = models.CharField(max_length=30, unique=True, editable=False)
    guest_name = models.CharField(max_length=150)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=50)
    guests_count = models.PositiveIntegerField(default=2)
    reservation_date = models.DateField()
    reservation_time = models.CharField(max_length=20)
    seating_area = models.ForeignKey(SeatingArea, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations')
    dining_experience = models.CharField(max_length=150, blank=True, default="A La Carte Experience")
    occasion = models.CharField(max_length=50, choices=OCCASION_CHOICES, default='casual')
    dietary_requests = models.TextField(blank=True, help_text="Allergies, vegetarian, vegan, halal preferences")
    special_requests = models.TextField(blank=True, help_text="Window booth, celebration dessert candle, sommelier pairing")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reservation_date', '-reservation_time', '-created_at']
        verbose_name_plural = "Table Reservations"

    def __str__(self):
        return f"{self.booking_reference} - {self.guest_name} ({self.guests_count} Guests on {self.reservation_date} at {self.reservation_time})"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = f"TC-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
