from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string

class User(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('delivery_partner', 'Delivery Partner'),
        ('admin', 'Admin'),
    ]

    mobile_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_mobile_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.mobile_number} - {self.get_role_display()}"

class OTP(models.Model):
    mobile_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def is_expired(self):
        expiry_time = self.created_at + timedelta(minutes=10)
        return timezone.now() > expiry_time

    @staticmethod
    def generate_otp():
        # Static OTP as per requirements
        return '1234'

    def __str__(self):
        return f"OTP for {self.mobile_number}: {self.otp_code}"
