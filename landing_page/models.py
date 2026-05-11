from django.db import models
from core.models import BaseModel


class SiteConfiguration(BaseModel):
    # Social URLs
    facebook_url = models.URLField(blank=True, default='')
    linkedin_url = models.URLField(blank=True, default='')
    twitter_url = models.URLField(blank=True, default='')
    email_address = models.EmailField(blank=True, default='')

    # App Store URLs
    app_store_url = models.URLField(blank=True, default='')
    play_store_url = models.URLField(blank=True, default='')

    # Stats
    stat_downloads_value = models.CharField(
        max_length=50, default='+0M', blank=True
    )
    stat_members_value = models.CharField(
        max_length=50, default='+0M', blank=True
    )
    stat_communities_value = models.CharField(
        max_length=50, default='+0K', blank=True
    )

    # Hero Section
    hero_title = models.CharField(
        max_length=255, verbose_name="Hero Main Title",
        default="Stress-free packing",
        help_text="The main heading text."
    )
    hero_subtitle_blue = models.CharField(
        max_length=255, verbose_name="Hero Highlighted Subtitle",
        default="for the whole family.",
        help_text="The blue highlighted text next to/below the title."
    )
    hero_description = models.TextField(
        verbose_name="Hero Description Text",
        default=(
            "Organize camp gear, travel essentials, and closet\n"
            "inventory with invisible AI. Built for busy parents\n"
            "who need simplicity, not another complex tool."
        ),
        help_text="The text under the title. Use Enter for new lines."
    )
    hero_desktop_image = models.ImageField(
        upload_to='site_images/', verbose_name="Hero Desktop Image",
        blank=True, null=True,
        help_text="The app preview image on desktop screens."
    )
    hero_mobile_frame_image = models.ImageField(
        upload_to='site_images/', verbose_name="Hero Mobile App Preview Image",
        blank=True, null=True,
        help_text="The mobile phone frame image."
    )

    # Features Section
    features_section_title = models.CharField(
        max_length=255, verbose_name="Features Section Main Title",
        default="Features", blank=True
    )
    
    # Feature 1
    feature_1_title = models.CharField(
        max_length=255, verbose_name="Feature 1 Title",
        default="Smart Closet Scanner", blank=True
    )
    feature_1_description = models.TextField(
        verbose_name="Feature 1 Description",
        default=(
            "Snap a photo of any item. Our AI automatically detects the "
            "type, size, and brand to build your inventory in seconds."
        ),
        blank=True
    )
    feature_1_image = models.ImageField(
        upload_to='site_images/', verbose_name="Feature 1 Image",
        blank=True, null=True
    )

    # Feature 2
    feature_2_title = models.CharField(
        max_length=255, verbose_name="Feature 2 Title",
        default="Family Accounts", blank=True
    )
    feature_2_description = models.TextField(
        verbose_name="Feature 2 Description",
        default=(
            "Seamlessly switch between children's profiles. Track\n"
            "what's in the closet for Leo and what's ready for Ava\n"
            "in one tap."
        ),
        blank=True
    )
    feature_2_image = models.ImageField(
        upload_to='site_images/', verbose_name="Feature 2 Image",
        blank=True, null=True
    )

    # Dynamic Packing Section
    packing_section_title = models.CharField(
        max_length=255, verbose_name="Packing Section Title",
        default="Dynamic Packing Lists", blank=True
    )
    packing_section_description = models.TextField(
        verbose_name="Packing Section Description",
        default=(
            "Smart lists that update based on weather, location. Never "
            "forget a\ntoothbrush (or a rain coat) again."
        ),
        blank=True
    )
    packing_section_image = models.ImageField(
        upload_to='site_images/', verbose_name="Packing Section Image",
        blank=True, null=True
    )


    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def __str__(self):
        return "Site Configuration"

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SiteConfiguration, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class ContactMessage(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


class Testimonial(BaseModel):
    author_name = models.CharField(max_length=100)
    author_role = models.CharField(max_length=100)
    author_location = models.CharField(max_length=100)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    avatar = models.ImageField(
        upload_to='testimonials/', blank=True, null=True
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.author_name} - {self.author_role}"
