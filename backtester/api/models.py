from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
# from django.contrib.auth.hashers import make_password

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class UserRegistration(AbstractBaseUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=15, blank=True, null=True)
    username = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_no']

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        # return self.is_superuser
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def last_login(self):
        return None

    # def set_password(self, raw_password):
    #     self.password = raw_password

    # def check_password(self, raw_password):
    #     return raw_password == self.password

    def save(self, *args, **kwargs):
        # if self.password:  # Check if password is provided
        #     self.set_password(self.password)  # Hash the password if provided
        #     self.password = None  # Set password to None to avoid storing plain text
        super().save(*args, **kwargs)

# class CustomUser(AbstractUser):
#     # Add any additional fields you need
#     bio = models.TextField(blank=True)
