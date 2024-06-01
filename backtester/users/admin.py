from django.contrib import admin
from .models import User, Webhook_urls
# Register your models here.
admin.site.register(User)
admin.site.register(Webhook_urls)