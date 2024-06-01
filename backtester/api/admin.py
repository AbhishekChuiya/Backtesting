from django.contrib import admin
from .models import UserRegistration

class UserRegistrationAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone_no', 'username']  # Add 'phone_no' to list_display

admin.site.register(UserRegistration, UserRegistrationAdmin)
