from django.db import models
from backtester.constants import user_type
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import AbstractUser

class UserManager(BaseUserManager):
    def create_user(self, email, name, phone_no, user_type, gst_no, pincode, pan_no, country, state, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phone_no=phone_no,
            user_type=user_type,
            gst_no=gst_no,
            pincode=pincode,
            pan_no=pan_no,
            country=country,
            state=state,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone_no, user_type, gst_no, pincode, pan_no, country, state, password):
        user = self.create_user(
            email=email,
            name=name,
            phone_no=phone_no,
            user_type=user_type,
            gst_no=gst_no,
            pincode=pincode,
            pan_no=pan_no,
            country=country,
            state=state,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=150,  blank=True, null=True)
    email = models.EmailField(max_length=150, unique=True)
    phone_no = models.CharField(max_length=14,  blank=True)
    user_type = models.CharField(choices=user_type, max_length=30, default='Customer')
    gst_no = models.CharField(max_length=100,  blank=True)
    pincode = models.IntegerField( blank=True, null=True)
    pan_no = models.CharField(max_length=100,  blank=True)
    country = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    reg_date = models.DateTimeField(auto_now_add=True,  blank=True, null=True)
    address = models.TextField(max_length=255, blank=True, null=True)
    # login_datetime= models.DateTimeField(null=True,blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone_no', 'user_type', 'gst_no', 'pincode', 'pan_no', 'country', 'state']

    objects = UserManager()
    
class Webhook_urls(models.Model):
    user= models.ForeignKey('users.user',on_delete=models.SET_NULL,null=True,blank=True)
    urls= models.URLField(blank=True,null=True)
    added_at= models.DateTimeField(auto_now=True,blank=True,null=True)


# class UserPayment(models.Model):
#     payment_id= models.CharField(max_length=80)