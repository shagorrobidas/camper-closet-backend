from django.db import models
from core.models import BaseModel
from django.conf import settings


class ItemCategoryType(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5)

    def __str__(self):
        return self.name


class ItemCategory(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=100
    )
    type = models.ForeignKey(
        ItemCategoryType,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    is_custom = models.BooleanField(
        default=False
    )
    is_system = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = ("user", "name", "type")
        indexes = [
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
    main_category = models.ForeignKey(
        ItemCategoryType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='closet_items_main'
    )
    sub_category = models.ForeignKey(
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
    color = models.JSONField(
        default=list,
        blank=True,
        help_text="Store multiple color codes or names as a JSON array"
    )
    size = models.CharField(
        max_length=100
    )
    quantity = models.IntegerField(
        default=1
    )
    notes = models.TextField(
        blank=True,
        null=True
    )
    is_scanned = models.BooleanField(
        default=False
    )
    is_favorite = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = ("user", "name")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["sub_category"]),
        ]

    def __str__(self):
        return self.name
