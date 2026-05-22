from django.db import models
from django.db.models import Sum
from django.utils import timezone
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
        on_delete=models.CASCADE,
        related_name='trips'
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
        ('None', 'None'),
    ]
    title = models.CharField(
        "Camp name",
        max_length=255
    )

    trip_type = models.ForeignKey(
        TripType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Camp Type"
    )

    season = models.CharField(
        max_length=20,
        choices=SEASON_CHOICES,
        default='Summer',
        null=True,
        blank=True
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    image = models.ImageField(
        verbose_name="Image",
        upload_to="packing_templates/",
        blank=True,
        null=True
    )

    sort_order = models.IntegerField(default=0, null=True, blank=True)

    is_system = models.BooleanField(default=True)

    @property
    def required_items_count(self):
        return self.items.filter(is_required=True, deleted_at__isnull=True).count()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Camp"
        verbose_name_plural = "Camps"


class PackingTemplateCategory(BaseModel):
    template = models.ForeignKey(
        PackingTemplate,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=255)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.template.title} - {self.name}"

    class Meta:
        verbose_name_plural = "Packing Template Categories"
        ordering = ['sort_order', 'created_at']


class PackingTemplateItem(BaseModel):

    template = models.ForeignKey(
        PackingTemplate,
        on_delete=models.CASCADE,
        related_name='items'
    )

    category = models.ForeignKey(
        PackingTemplateCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items'
    )

    brand_category = models.ForeignKey(
        'dashboard.BrandCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Sentences"
    )

    show_shop_url = models.BooleanField(default=False, verbose_name="Shop Now Enable")

    title = models.CharField(max_length=255, blank=True, null=True)

    quantity = models.IntegerField(default=0)

    is_required = models.BooleanField(default=True)

    note = models.TextField(blank=True, null=True)

    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['title']

    def __str__(self):
        if self.title:
            return f"{self.template.title} - {self.title}"
        return f"{self.template.title} - Item {self.id}"


class TripPackingItem(BaseModel):
    PACKING_STATUS_CHOICES = [
        ('active', 'Active'),
        ('complete', 'Complete'),
        ('archived', 'Archived'),
    ]

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='packing_items',
        null=True,
        blank=True
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

    title = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

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

    category = models.ForeignKey(
        PackingTemplateCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trip_items'
    )

    quantity = models.IntegerField(
        default=0,
        null=True,
        blank=True
    )
    picked_quantity = models.IntegerField(
        default=0,
        null=True,
        blank=True
    )

    is_required = models.BooleanField(
        default=True,
        null=True,
        blank=True
    )

    is_packed = models.BooleanField(
        default=False,
        null=True,
        blank=True
    )

    packed_at = models.DateTimeField(null=True, blank=True)

    is_custom_item = models.BooleanField(default=False)

    note = models.TextField(blank=True, null=True)

    sort_order = models.IntegerField(default=0)

    def __str__(self):
        if self.title:
            return self.title
        return self.sub_category.name if self.sub_category else "Uncategorized Item" # noqa

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        update_fields = kwargs.get('update_fields')
        if update_fields:
            status_fields = {
                'picked_quantity',
                'is_packed',
                'is_required',
                'packed_at'
            }
            if all(f in status_fields for f in update_fields):
                super().save(*args, **kwargs)
                return

        super().save(*args, **kwargs)
        if not is_new:
            # If not new, quantity might have changed, so refresh status
            # refresh_status also saves, but only update_fields
            self.refresh_status()

    @property
    def remaining_quantity(self):
        return max(0, self.quantity - self.picked_quantity)

    def refresh_status(self):
        """Recalculate picked_quantity and packed status from selections."""
        result = self.selections.aggregate(total=Sum('quantity'))
        total_picked = result['total'] or 0

        self.picked_quantity = total_picked
        if total_picked >= self.quantity:
            self.is_packed = True
            self.is_required = False  # As requested: when quantity == picked_quantity, is_required false  # noqa
            if not self.packed_at:
                self.packed_at = timezone.now()
        else:
            self.is_packed = False
            self.is_required = True  # Revert if it's no longer fully picked  # noqa
            self.packed_at = None
        self.save(
            update_fields=[
                'picked_quantity',
                'is_packed',
                'is_required',
                'packed_at'
            ]
        )


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
    quantity = models.IntegerField(default=0)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.closet_item.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.packing_item.refresh_status()

    def delete(self, *args, **kwargs):
        packing_item = self.packing_item
        super().delete(*args, **kwargs)
        packing_item.refresh_status()


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
