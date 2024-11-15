# users/models.py

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator


class UserType(models.IntegerChoices):
    INSTRUCTOR = 1, 'Instructor'
    CLIENT = 2, 'Client'

class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username is required.")
        if not email:
            raise ValueError("The Email is required.")
        if not extra_fields.get('phone_number'):
            raise ValueError("The Phone Number is required.")

        email = self.normalize_email(email)
        phone_number = extra_fields.pop('phone_number')
        user = self.model(username=username, email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', UserType.INSTRUCTOR)

        return self.create_user(phone_number=phone_number, email=email, password=password, **extra_fields)


class User(AbstractUser):
    user_type = models.IntegerField(choices=UserType.choices, default=UserType.CLIENT)
    bio = models.TextField(blank=True, null=True)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, unique=True, help_text="Enter a valid phone number."
    )

    objects = UserManager()

    REQUIRED_FIELDS = ['email','username' ]
    USERNAME_FIELD = 'phone_number'
    EMAIL_FIELD = 'email'

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
