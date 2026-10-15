from django.db import models

class ContactInfo(models.Model):
    restaurant_name = models.CharField(max_length=150, default="The Chesterfield - Kitchen & Bar")
    tagline = models.CharField(max_length=200, default="We welcome you to our Victorian dining hall on historic King Street.")
    address = models.CharField(max_length=255, default="56 King Street")
    city = models.CharField(max_length=100, default="Manchester")
    postcode = models.CharField(max_length=20, default="M2 4WU")
    country = models.CharField(max_length=100, default="United Kingdom")
    phone = models.CharField(max_length=50, default="0161 839 0640")
    phone_secondary = models.CharField(max_length=50, blank=True, default="+44 (0) 161 839 0641")
    email = models.EmailField(default="reservations@chesterfield-restaurant.co.uk")
    email_events = models.EmailField(blank=True, default="events@chesterfield-restaurant.co.uk")
    
    opening_mon_thu = models.CharField(max_length=100, default="12:00 PM – 10:00 PM")
    opening_fri_sat = models.CharField(max_length=100, default="12:00 PM – 11:30 PM")
    opening_sun = models.CharField(max_length=100, default="12:00 PM – 9:30 PM (Sunday Roast)")
    
    dress_code = models.CharField(max_length=200, default="Smart Casual • Elegant attire recommended • No athletic wear after 6 PM")
    parking_info = models.TextField(default="Valet service available from 5:30 PM on King Street. Nearest secure multi-storey parking at Q-Park Deansgate (3 minutes walk).")
    map_embed_url = models.TextField(
        default="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2374.3168676251547!2d-2.2476561233061694!3d53.48128507232863!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x487bb1c20141bb0b%3A0xe54d6fa4d033a0b1!2sKing%20St%2C%20Manchester%2C%20UK!5e0!3m2!1sen!2s!4v1700000000000!5m2!1sen!2s",
        help_text="Google Maps Embed URL iframe src"
    )
    
    hero_image = models.ImageField(upload_to='contact/', blank=True, null=True)
    static_hero_image = models.CharField(max_length=255, default='contact/media/contact_hero.jpg')

    class Meta:
        verbose_name_plural = "Contact Information & Location"

    def __str__(self):
        return f"{self.restaurant_name} ({self.city})"

    def get_hero_image(self):
        if self.hero_image:
            return self.hero_image.url
        return f"/static/{self.static_hero_image}"


class ContactDepartment(models.Model):
    name = models.CharField(max_length=150)
    role_description = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name_plural = "Contact Departments"

    def __str__(self):
        return self.name


class ContactFAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name_plural = "Frequently Asked Questions (FAQ)"

    def __str__(self):
        return self.question


class ContactMessage(models.Model):
    INQUIRY_CHOICES = [
        ('general', 'General Inquiry'),
        ('reservation', 'Table Reservation Assistance'),
        ('private_dining', 'Private Dining & Events'),
        ('press', 'Press, Media & Collaborations'),
        ('careers', 'Careers & Brigade Opportunities'),
        ('feedback', 'Guest Experience Feedback'),
    ]

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    inquiry_type = models.CharField(max_length=50, choices=INQUIRY_CHOICES, default='general')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Guest Contact Messages / Inquiries"

    def __str__(self):
        return f"{self.full_name} - {self.subject} ({self.created_at.strftime('%d %b %Y')})"
