from rest_framework import serializers
import re
from django.contrib.auth.password_validation import validate_password

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    phone_number = serializers.CharField(
        source="phone",
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=15,
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
            "phone_number",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
        }

    def validate_email(self, value):
        value = value.strip().lower()
        user = User.objects.filter(email=value).first()
        if user and user.is_verified:
            raise serializers.ValidationError("A verified account with this email already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)

       
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("Password must include at least one lowercase letter.")
        if not re.search(r"\d", value):
            raise serializers.ValidationError("Password must include at least one number.")
        if not re.search(r"[^\w\s]", value):
            raise serializers.ValidationError("Password must include at least one special character.")
        return value

    def validate_phone_number(self, value):
        if value in (None, ""):
            return value

        phone = value.strip()
        if not re.fullmatch(r"^\d{10,15}$", phone):
            raise serializers.ValidationError(
                "Phone number must be 10 to 15 digits."
            )
        return phone

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs




class VerifyOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[])

    class Meta:
        model = User
        fields = ["email", "otp"]
        extra_kwargs = {
            "otp": {"min_length": 6, "max_length": 6},
        }

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found for this email.")
        return value


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[])

    class Meta:
        model = User
        fields = ["email", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_email(self, value):
        return value.strip().lower()
