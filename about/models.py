from django.db import models

class TeamMember(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    bio = models.TextField()
    image = models.ImageField(upload_to='team/', blank=True, null=True)
    static_image = models.CharField(max_length=255, blank=True, null=True)
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

    def __str__(self):
        return f"{self.year}: {self.title}"
