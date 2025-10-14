# Common utility functions for the Food Delivery App

import random
import string
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class ResponseHandler:
    """Standardized response handler for API endpoints"""

    @staticmethod
    def success(message="Success", data=None, status=200):
        """Return standardized success response"""
        response = {
            'status': 'success',
            'message': message,
            'timestamp': timezone.now().isoformat()
        }
        if data:
            response['data'] = data
        return JsonResponse(response, status=status)

    @staticmethod
    def error(message="Error occurred", errors=None, status=400):
        """Return standardized error response"""
        response = {
            'status': 'error',
            'message': message,
            'timestamp': timezone.now().isoformat()
        }
        if errors:
            response['errors'] = errors
        return JsonResponse(response, status=status)

    @staticmethod
    def validation_error(errors, status=400):
        """Return validation error response"""
        return ResponseHandler.error(
            message="Validation failed",
            errors=errors,
            status=status
        )

class OTPHandler:
    """Reusable OTP handling functionality"""

    @staticmethod
    def generate_otp(length=4):
        """Generate random OTP of specified length"""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def is_otp_valid(otp_obj, expiry_minutes=10):
        """Check if OTP is still valid"""
        if not otp_obj or otp_obj.is_verified:
            return False

        expiry_time = otp_obj.created_at + timedelta(minutes=expiry_minutes)
        return timezone.now() <= expiry_time

    @staticmethod
    def send_otp_sms(mobile_number, otp_code):
        """Send OTP via SMS (mock implementation)"""
        # In production, integrate with SMS service like Twilio, AWS SNS, etc.
        print(f"SMS: Your OTP is {otp_code}. Valid for 10 minutes.")
        return True

class ValidationUtils:
    """Common validation utilities"""

    @staticmethod
    def validate_mobile_number(mobile_number):
        """Validate Indian mobile number format"""
        if not mobile_number:
            raise ValidationError("Mobile number is required")

        # Remove any non-digit characters
        clean_mobile = ''.join(filter(str.isdigit, mobile_number))

        if len(clean_mobile) != 10:
            raise ValidationError("Mobile number must be 10 digits")

        if not clean_mobile.startswith(('6', '7', '8', '9')):
            raise ValidationError("Invalid mobile number format")

        return clean_mobile

    @staticmethod
    def validate_otp(otp_code):
        """Validate OTP format"""
        if not otp_code:
            raise ValidationError("OTP is required")

        if len(otp_code) != 4 or not otp_code.isdigit():
            raise ValidationError("OTP must be 4 digits")

        return otp_code

    @staticmethod
    def validate_address(address, field_name="Address"):
        """Validate address field"""
        if not address or len(address.strip()) < 10:
            raise ValidationError(f"{field_name} must be at least 10 characters long")

        return address.strip()

class PermissionUtils:
    """Reusable permission checking utilities"""

    @staticmethod
    def check_user_role(user, allowed_roles):
        """Check if user has required role"""
        if not user or not user.is_authenticated:
            return False

        if isinstance(allowed_roles, str):
            allowed_roles = [allowed_roles]

        return user.role in allowed_roles

    @staticmethod
    def check_booking_access(user, booking):
        """Check if user can access specific booking"""
        if user.role == 'admin':
            return True
        elif user.role == 'customer' and booking.customer == user:
            return True
        elif user.role == 'delivery_partner' and booking.delivery_partner == user:
            return True

        return False

class DateTimeUtils:
    """DateTime utility functions"""

    @staticmethod
    def format_datetime(dt, format_type='default'):
        """Format datetime for display"""
        if not dt:
            return ""

        formats = {
            'default': '%Y-%m-%d %H:%M:%S',
            'date_only': '%Y-%m-%d',
            'time_only': '%H:%M:%S',
            'display': '%d %b %Y, %I:%M %p',
            'short': '%d/%m/%Y %H:%M'
        }

        return dt.strftime(formats.get(format_type, formats['default']))

    @staticmethod
    def get_time_difference(start_time, end_time=None):
        """Calculate time difference"""
        if end_time is None:
            end_time = timezone.now()

        diff = end_time - start_time

        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60

        if days > 0:
            return f"{days} days, {hours} hours"
        elif hours > 0:
            return f"{hours} hours, {minutes} minutes"
        else:
            return f"{minutes} minutes"

def parse_json_safely(request):
    """Safely parse JSON from request body"""
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        raise ValidationError("Invalid JSON format")

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_user_activity(user, action, details=None):
    """Log user activity (can be extended with proper logging)"""
    log_message = f"User {user.mobile_number} ({user.role}): {action}"
    if details:
        log_message += f" - {details}"

    print(f"[{timezone.now()}] {log_message}")
    # In production, use proper logging framework
