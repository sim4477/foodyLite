from rest_framework import serializers
from .models import User, OTP

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile_number', 'role', 'is_mobile_verified', 'created_at']
        read_only_fields = ['id', 'created_at']

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['mobile_number', 'otp_code', 'created_at', 'is_verified']
        read_only_fields = ['created_at', 'is_verified']
