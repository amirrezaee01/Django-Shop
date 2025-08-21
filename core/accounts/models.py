from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from .validators import validate_iranian_phone_number


class UserType(models.IntegerChoices):
    customer = 1, _('Customer')
    admin = 2, _('Admin')
    superuser = 3, _('Superuser')


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('type', UserType.superuser.value)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_("email address",), unique=True)
    is_staff = models.BooleanField(default=False,)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    type = models.IntegerField(
        choices=UserType.choices, default=UserType.customer.value)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(
        'User', on_delete=models.CASCADE, related_name='user_profile')

    id = models.PositiveIntegerField(primary_key=True)  # Use user.id as PK

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[validate_iranian_phone_number],
        blank=True
    )
    image = models.ImageField(
        upload_to='profile_images/',
        default='profile_images/profile/default.png',
        blank=True,

    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def get_fullname(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return "کاربر جدید"

    def save(self, *args, **kwargs):
        if not self.id and self.user:
            self.id = self.user.id  # Set profile.id = user.id
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created and instance.type in [UserType.customer.value, UserType.admin.value]:
        Profile.objects.create(user=instance, id=instance.id)
