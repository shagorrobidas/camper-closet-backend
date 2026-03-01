from django.db import models
from core.models import BaseModel
from django.conf import settings


class BrandCategoryType(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5)

    def __str__(self):
        return self.name


class ItemCategory(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(
        max_length=100
    )
    type = models.ForeignKey(
        BrandCategoryType,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    is_custom = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = ("user", "name")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["type"]),
        ]

    def __str__(self):
        return self.name


class ClosetItem(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='closet_items'
    )
    category = models.ForeignKey(
        ItemCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='closet_items'
    )
    name = models.CharField(
        max_length=100
    )
    image = models.ImageField(
        upload_to='closet_items',
        blank=True,
        null=True
    )
    brand = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    color = models.CharField(
        max_length=100
    )
    size = models.CharField(
        max_length=100
    )
    quantity = models.IntegerField(
        default=1
    )
    note = models.TextField(
        blank=True,
        null=True
    )
    ai_detected = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = ("user", "name")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.name
