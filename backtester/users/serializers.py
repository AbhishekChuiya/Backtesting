from users.models import User
from rest_framework import serializers
from rest_framework.serializers import (Serializer, EmailField, CharField, ValidationError, ModelSerializer, SerializerMethodField)


class UserUpdateSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'is_staff', 'reg_date', 'is_active', 'is_superuser', 'user_type', 'groups', 'user_permissions', 'last_login']
        read_only_fields = ['email']
