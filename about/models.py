from django.db import models

class TeamMember(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    bio = models.TextField()
    image = models.ImageField(upload_to='team/', blank=True, null=True)
    static_image = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. about/media/chef_arthur.jpg")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.name} - {self.role}"

    def get_image_url(self):
        if self.image:
            return self.image.url
        if self.static_image:
            return f"/static/{self.static_image}"
        return "/static/about/media/chef_arthur.jpg"


class AboutStat(models.Model):
    number = models.CharField(max_length=50, help_text="e.g. 15+, 100%, 250+, 4.9★")
    label = models.CharField(max_length=150, help_text="e.g. Years of Culinary Craft")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name_plural = "About Stats"

    def __str__(self):
        return f"{self.number} - {self.label}"


class Milestone(models.Model):
    year = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'year']
        verbose_name_plural = "Milestones / Journey"

    def __str__(self):
        return f"{self.year}: {self.title}"


class Pillar(models.Model):
    number = models.CharField(max_length=10, default="01", help_text="e.g. 01, 02, 03")
    title = models.CharField(max_length=150)
    description = models.TextField()
    feature_1 = models.CharField(max_length=150, blank=True)
    feature_2 = models.CharField(max_length=150, blank=True)
    feature_3 = models.CharField(max_length=150, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name_plural = "Pillars / Core Values"

    def __str__(self):
        return f"{self.number} - {self.title}"


class AboutStory(models.Model):
    tagline = models.CharField(max_length=100, default="OUR STORY & PHILOSOPHY")
    heading = models.CharField(max_length=200, default="Where Seasonal Terroir Meets Contemporary Elegance")
    lead_paragraph = models.TextField(help_text="Primary highlighted paragraph")
    body_paragraph = models.TextField(help_text="Detailed story paragraph")
    quote_text = models.TextField(help_text="Chef's inspirational quote")
    quote_author = models.CharField(max_length=100, default="Arthur Pendelton")
    quote_author_title = models.CharField(max_length=150, default="Executive Head Chef & Co-Founder")
    primary_image = models.ImageField(upload_to='about/', blank=True, null=True)
    secondary_image = models.ImageField(upload_to='about/', blank=True, null=True)
    primary_static_image = models.CharField(max_length=255, default='about/media/chef_story.jpg')
    secondary_static_image = models.CharField(max_length=255, default='about/media/restaurant_interior.jpg')

    class Meta:
        verbose_name_plural = "About Story & Philosophy"

    def __str__(self):
        return self.heading

    def get_primary_image(self):
        if self.primary_image:
            return self.primary_image.url
        return f"/static/{self.primary_static_image}"

    def get_secondary_image(self):
        if self.secondary_image:
            return self.secondary_image.url
        return f"/static/{self.secondary_static_image}"
