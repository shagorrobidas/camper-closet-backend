from django.db import models
from django.contrib.auth.models import(
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from core.models import BaseModel
from django.utils import timezone
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
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
    date_of_birth = models.DateField(
        blank=True,
        null=True
    )
    is_email_verified = models.BooleanField(
        default=False
    )
    new_email = models.EmailField(
        unique=True,
        blank=True,
        null=True
    )
    firebase_uid = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True
    )
    auth_provider = models.CharField(
        max_length=50,
        default='email'
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

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        related_query_name='user',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        related_query_name='user',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email


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


# class EmailVerification(models.Model):
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE
#     )
#     token = models.UUIDField(
#         default=uuid.uuid4,
#         unique=True
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()

#     def is_valid(self):
#         return timezone.now() <= self.expires_at
