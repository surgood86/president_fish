import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.urls import reverse


class UserManager(BaseUserManager):
    def _create_user(self, phone_number, password, first_name=None, last_name=None, **extra_fields):
        """Create and save user with given phone_number, first_name and last_name"""
        if not phone_number:
            raise ValueError('The given phone number must be set')
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        user = self.model(phone_number=phone_number, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, first_name=None, last_name=None, **extra_fields):
        """Create and save a regular User with the given phone_number, first_name and last_name."""
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, first_name, last_name, **extra_fields)

    def create_superuser(self, phone_number, password, **extra_fields):
        """Create and save a SuperUser with the giver phone_number, first_name"""
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_active') is not True:
            raise ValueError('SuperUser must have is_active=True')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('SuperUser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('SuperUser must have is_superuser=True.')

        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    phone_regex = RegexValidator(
        regex=r'^\d{10,10}$',
        message="Phone number must be entered in the format: '0000000000'. Up to 10 digits allowed.")

    phone_number = models.CharField(validators=[phone_regex], max_length=10, unique=True, editable=True)

    first_name = models.CharField(max_length=50, null=True, blank=True, editable=True)
    last_name = models.CharField(max_length=50, null=True, blank=True, editable=True)

    code = models.CharField(max_length=5, null=True, blank=True, editable=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'

    objects = UserManager()

    def __str__(self):
        return self.phone_number

    def get_short_name(self):
        return self.first_name

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_absolute_url(self):
        return reverse('detail_user', args=[str(self.id)])
