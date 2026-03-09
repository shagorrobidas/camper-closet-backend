from django.db import models
from core.models import BaseModel
from users.models import User
from closet.models import ItemCategory, ClosetItem


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


class TripStatus(BaseModel):

    name = models.CharField(max_length=255)
    code = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    description = models.TextField(blank=True, null=True)

    sort_order = models.IntegerField(default=0)

    is_final = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Trip(BaseModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

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
    

    status = models.ForeignKey(
        TripStatus,
        on_delete=models.SET_NULL,
        null=True
    )

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


class PackingTemplateSeason(BaseModel):

    name = models.CharField(max_length=255)
    code = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    sort_order = models.IntegerField(
        default=0
    )

    def __str__(self):
        return self.name


class PackingTemplate(BaseModel):

    trip_type = models.ForeignKey(
        TripType,
        on_delete=models.CASCADE
    )

    season = models.ForeignKey(
        PackingTemplateSeason,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
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

    def __str__(self):
        return self.title


class PackingTemplateCategory(BaseModel):

    template = models.ForeignKey(
        PackingTemplate,
        on_delete=models.CASCADE
    )

    item_category = models.ForeignKey(
        ItemCategory,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=255)

    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class PackingTemplateItem(BaseModel):

    template = models.ForeignKey(
        PackingTemplate,
        on_delete=models.CASCADE
    )

    template_category = models.ForeignKey(
        PackingTemplateCategory,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=255)

    quantity = models.IntegerField(default=1)

    is_required = models.BooleanField(default=True)

    sort_order = models.IntegerField(default=0)

    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class PackingList(BaseModel):

    trip = models.OneToOneField(
        Trip,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class PackingListItem(BaseModel):

    packing_list = models.ForeignKey(
        PackingList,
        on_delete=models.CASCADE
    )

    closet_item = models.ForeignKey(
        ClosetItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        ItemCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=255, blank=True, null=True)

    quantity = models.IntegerField(default=1)

    is_packed = models.BooleanField(default=False)

    packed_at = models.DateTimeField(null=True, blank=True)

    is_custom_item = models.BooleanField(default=False)

    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name or (self.closet_item.name if self.closet_item else "Unnamed Item")