from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserRegistration  # Import your custom user model
from users.models import User
# from .models import CustomUser

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

class UserSignUpSerializer(serializers.ModelSerializer):
    phone_no = serializers.CharField(max_length=15, required=False)
    password2 = serializers.CharField(write_only=True)
    class Meta:
        # model = get_user_model()
        # model = UserRegistration
        model = User
        fields = ['email', 'name', 'phone_no', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError("Passwords do not match.")
        return data


    def create(self, validated_data):
        phone_no = validated_data.pop('phone_no', None)
        password = validated_data.pop('password', None)
        password2 = validated_data.pop('password2', None)
        
        user = User.objects.create(**validated_data)
        # user = UserRegistration.objects.create(**validated_data)
        # user = get_user_model().objects.create(**validated_data)
        
        if phone_no:
            user.phone_no = phone_no
            user.save(update_fields=['phone_no'])
        if password and password2:
            user.set_password(password)  # Set and hash the password
            user.save(update_fields=['password'])  # Save only the password field
        
        return user

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # if not UserRegistration.objects.filter(email=value).exists():
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8)

# class UserSerializer(serializers.Serializer):
#     class Meta:
#         model = CustomUser
#         fields = ['id', 'username', 'email', 'bio']

# class JSONtoCSVSerializer(serializers.Serializer):
#     data = serializers.JSONField()
