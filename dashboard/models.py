from django.db import models
from core.models import BaseModel


class BrandCategory(BaseModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class ShopWebsite(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    website_url = models.URLField(max_length=500, blank=True, null=True)

    # multiple select (like "Shop Camp Stores")
    categories = models.ManyToManyField(
        BrandCategory,
        related_name='shop_websites',
        blank=True
    )

    image = models.ImageField(
        upload_to='shop_websites/',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
