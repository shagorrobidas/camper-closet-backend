from django.db import models
from core.models import BaseModel
from users.models import User
from closet.models import ItemCategory, ClosetItem, ItemCategoryType


class TripType(BaseModel):

    name = models.CharField(max_length=255)
    code = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Trip(BaseModel):
    TRIP_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Complete', 'Complete'),
        ('Past', 'Past'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    template = models.ForeignKey(
        "PackingTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    trip_type = models.ForeignKey(
        TripType,
        on_delete=models.SET_NULL,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=TRIP_STATUS_CHOICES,
        default='Active'
    )

    is_template_applied = models.BooleanField(default=False)

    name = models.CharField(max_length=255)

    location = models.CharField(max_length=255)

    start_date = models.DateField()
    end_date = models.DateField()

    packing_deadline = models.DateField(
        null=True,
        blank=True
    )

    note = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class PackingTemplate(BaseModel):
    SEASON_CHOICES = [
        ('Summer', 'Summer'),
        ('Winter', 'Winter'),
        ('Rainy', 'Rainy'),
        ('Autumn', 'Autumn'),
        ('Late Autumn', 'Late Autumn'),
        ('Spring', 'Spring'),
    ]
    title = models.CharField(
        max_length=255
    )

    trip_type = models.ForeignKey(
        TripType,
        on_delete=models.CASCADE
    )

    season = models.CharField(
        max_length=20,
        choices=SEASON_CHOICES,
        default='Summer'
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    image = models.ImageField(
        upload_to="packing_templates/",
        blank=True,
        null=True
    )

    sort_order = models.IntegerField(default=0)

    is_system = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class PackingTemplateItem(BaseModel):

    template = models.ForeignKey(
        PackingTemplate,
        on_delete=models.CASCADE,
        related_name='items'
    )

    main_category = models.ForeignKey(
        ItemCategoryType,
        on_delete=models.CASCADE
    )

    sub_category = models.ForeignKey(
        ItemCategory,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255, blank=True, null=True)

    quantity = models.IntegerField(default=1)

    is_required = models.BooleanField(default=True)

    note = models.TextField(blank=True, null=True)

    sort_order = models.IntegerField(default=0)

    def __str__(self):
        if self.title:
            return self.template.title + " - " + self.title
        return self.template.title + " - " + self.sub_category.name


class TripPackingItem(BaseModel):
    PACKING_STATUS_CHOICES = [
        ('active', 'Active'),
        ('complete', 'Complete'),
        ('archived', 'Archived'),
    ]

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='packing_items'
    )

    main_category = models.ForeignKey(
        ItemCategoryType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    sub_category = models.ForeignKey(
        ItemCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    title = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=PACKING_STATUS_CHOICES,
        default='active'
    )
    
    template_item = models.ForeignKey(
        PackingTemplateItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    quantity = models.IntegerField(default=1)
    picked_quantity = models.IntegerField(default=0)

    is_required = models.BooleanField(default=True)

    is_packed = models.BooleanField(default=False)

    packed_at = models.DateTimeField(null=True, blank=True)

    is_custom_item = models.BooleanField(default=False)

    note = models.TextField(blank=True, null=True)

    sort_order = models.IntegerField(default=0)

    def __str__(self):
        if self.title:
            return self.title
        return self.sub_category.name if self.sub_category else "Uncategorized Item"


class TripPackingItemSelection(BaseModel):
    packing_item = models.ForeignKey(
        TripPackingItem,
        on_delete=models.CASCADE,
        related_name='selections'
    )
    closet_item = models.ForeignKey(
        ClosetItem,
        on_delete=models.CASCADE,
        related_name='packing_selections'
    )
    quantity = models.IntegerField(default=1)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.closet_item.name}"


class TripEvent(BaseModel):
    EVENT_TYPE_CHOICES = [
        ('deadline', 'Deadline'),
        ('trip_start', 'Trip Start'),
        ('trip_end', 'Trip End'),
        ('custom', 'Custom'),
    ]

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='events'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default='custom'
    )
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.title} - {self.trip.name}"