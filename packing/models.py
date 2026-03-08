from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from core.models import BaseModel


class PackingTemplateSeason(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active", "sort_order"]),
        ]

    def __str__(self):
        return self.name


class PackingTemplate(BaseModel):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="packing_templates",
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    trip_type = models.ForeignKey(
        "trips.TripType",
        on_delete=models.PROTECT,
        related_name="packing_templates",
    )
    season = models.ForeignKey(
        PackingTemplateSeason,
        on_delete=models.PROTECT,
        related_name="packing_templates",
    )
    is_public = models.BooleanField(default=False)
    is_system_template = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["creator"]),
            models.Index(fields=["trip_type"]),
            models.Index(fields=["season"]),
            models.Index(fields=["is_public"]),
            models.Index(fields=["is_system_template"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return self.title


class PackingTemplateItem(BaseModel):
    template = models.ForeignKey(
        PackingTemplate,
        on_delete=models.CASCADE,
        related_name="items",
    )
    category = models.ForeignKey(
        "closet.ItemCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="template_items",
    )
    name = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    is_required = models.BooleanField(default=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["template"]),
            models.Index(fields=["category"]),
            models.Index(fields=["name"]),
            models.Index(fields=["template", "name"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.template.title}"


class PackingListStatus(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_final = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active", "sort_order"]),
            models.Index(fields=["is_final"]),
        ]

    def __str__(self):
        return self.name


class PackingList(BaseModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="packing_lists",
    )
    trip = models.OneToOneField(
        "trips.Trip",
        on_delete=models.CASCADE,
        related_name="packing_list",
    )
    status = models.ForeignKey(
        PackingListStatus,
        on_delete=models.PROTECT,
        related_name="packing_lists",
    )
    title = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["owner"]),
            models.Index(fields=["trip"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["owner", "status"]),
        ]

    def __str__(self):
        return self.title

    @property
    def total_items(self):
        return self.items.count()

    @property
    def packed_items(self):
        return self.items.filter(is_packed=True).count()

    @property
    def progress_percentage(self):
        total = self.total_items
        if total == 0:
            return 0
        return round((self.packed_items / total) * 100, 2)


class PackingListItem(BaseModel):
    packing_list = models.ForeignKey(
        PackingList,
        on_delete=models.CASCADE,
        related_name="items",
    )
    closet_item = models.ForeignKey(
        "closet.ClosetItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="packing_items",
    )
    category = models.ForeignKey(
        "closet.ItemCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="packing_list_items",
    )
    name = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    is_packed = models.BooleanField(default=False)
    packed_at = models.DateTimeField(blank=True, null=True)
    is_custom_item = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["packing_list"]),
            models.Index(fields=["closet_item"]),
            models.Index(fields=["category"]),
            models.Index(fields=["is_packed"]),
            models.Index(fields=["packing_list", "is_packed"]),
        ]

    def __str__(self):
        return self.name

    def mark_packed(self):
        self.is_packed = True
        self.packed_at = timezone.now()
        self.save(update_fields=["is_packed", "packed_at", "updated_at"])

    def mark_unpacked(self):
        self.is_packed = False
        self.packed_at = None
        self.save(update_fields=["is_packed", "packed_at", "updated_at"])