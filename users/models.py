from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from core.models import BaseModel
from django.utils import timezone
import uuid


class AuthProvider(models.TextChoices):
    EMAIL = 'email', 'Email'
    GOOGLE = 'google', 'Google'
    APPLE = 'apple', 'Apple'


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_parent(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", "parent")
        return self.create_user(email, password, **extra_fields)

    def create_child(self, email, parent, password=None, **extra_fields):
        extra_fields.setdefault("role", "child")
        extra_fields.setdefault("parent", parent)
        return self.create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_email_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):

    ROLE_CHOICES = (
        ('parent', 'Parent'),
        ('child', 'Child'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    full_name = models.CharField(
        max_length=100
    )
    email = models.EmailField(
        unique=True
    )
    profile_pic = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )
    profile_pic_url = models.URLField(
        max_length=500,
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True
    )
    is_email_verified = models.BooleanField(
        default=False
    )
    firebase_uid = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True
    )
    auth_provider = models.CharField(
        max_length=50,
        choices=AuthProvider.choices,
        default=AuthProvider.EMAIL
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True
    )

    is_staff = models.BooleanField(
        default=False
    )
    is_superuser = models.BooleanField(
        default=False
    )
    last_logout = models.DateTimeField(
        null=True,
        blank=True
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        related_query_name='user',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', # noqa
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        related_query_name='user',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
        ]

    @property
    def is_parent(self):
        return self.role == 'parent'

    @property
    def is_child(self):
        return self.role == 'child'

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=(
        ('email_verification', 'Email Verification'),
        ('password_reset', 'Password Reset'),
        ('login', 'Login'),
        ('change_email', 'Change Email'),

    ))
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() <= self.expires_at

    class Meta:
        indexes = [
            models.Index(fields=['user', 'purpose']),
        ]


class EmailVerification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() <= self.expires_at


class Notification(BaseModel):
    NOTIFICATION_TYPE_CHOICES = [
        ('system', 'System'),
        ('reminder', 'Reminder'),
        ('alert', 'Alert'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='system'
    )
    reference_id = models.CharField(max_length=255, blank=True, null=True)
    reference_type = models.CharField(max_length=100, blank=True, null=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.user.email}"


class NotificationSetting(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )
    enabled = models.BooleanField(default=True)
    packing_reminders = models.BooleanField(default=True)
    milestone_achievements = models.BooleanField(default=True)
    weekly_summaries = models.BooleanField(default=True)

    def __str__(self):
        return f"Settings for {self.user.email}"
