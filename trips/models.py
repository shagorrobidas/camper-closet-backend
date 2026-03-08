from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from core.models import BaseModel


class TripType(BaseModel):
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


class TripStatus(BaseModel):
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


class Trip(BaseModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trips",
    )
    assigned_child = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_trips",
    )
    trip_type = models.ForeignKey(
        TripType,
        on_delete=models.PROTECT,
        related_name="trips",
    )
    status = models.ForeignKey(
        TripStatus,
        on_delete=models.PROTECT,
        related_name="trips",
    )
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    packing_deadline = models.DateField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["owner"]),
            models.Index(fields=["assigned_child"]),
            models.Index(fields=["trip_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["start_date"]),
            models.Index(fields=["end_date"]),
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["owner", "start_date"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be earlier than start date.")

        if self.packing_deadline and self.packing_deadline > self.start_date:
            raise ValidationError("Packing deadline cannot be after trip start date.")

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1


