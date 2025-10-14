# Reusable mixins and base classes for Django views

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.utils import timezone
from .utils import ResponseHandler, PermissionUtils, ValidationUtils, parse_json_safely, log_user_activity

User = get_user_model()

class JSONResponseMixin:
    """Mixin to handle JSON responses consistently"""

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            return ResponseHandler.error(str(e), status=500)

class RoleRequiredMixin:
    """Mixin to check user roles"""
    required_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not PermissionUtils.check_user_role(request.user, self.required_roles):
            return ResponseHandler.error(
                "Insufficient permissions", 
                status=403
            )
        return super().dispatch(request, *args, **kwargs)

class BookingAccessMixin:
    """Mixin to check booking access permissions"""

    def get_booking_or_403(self, booking_id, user):
        """Get booking or return 403 if no access"""
        try:
            from apps.booking.models import Booking
            booking = Booking.objects.get(id=booking_id)

            if not PermissionUtils.check_booking_access(user, booking):
                return None, ResponseHandler.error("Access denied", status=403)

            return booking, None
        except Booking.DoesNotExist:
            return None, ResponseHandler.error("Booking not found", status=404)

@method_decorator(csrf_exempt, name='dispatch')
class BaseAPIView(JSONResponseMixin, LoginRequiredMixin, View):
    """Base API view with common functionality"""

    def get_json_data(self):
        """Get and validate JSON data from request"""
        try:
            return parse_json_safely(self.request)
        except Exception as e:
            return None

    def log_activity(self, action, details=None):
        """Log user activity"""
        log_user_activity(self.request.user, action, details)

class CustomerRequiredView(RoleRequiredMixin, BaseAPIView):
    """Base view for customer-only endpoints"""
    required_roles = ['customer']

class DeliveryPartnerRequiredView(RoleRequiredMixin, BaseAPIView):
    """Base view for delivery partner-only endpoints"""
    required_roles = ['delivery_partner']

class AdminRequiredView(RoleRequiredMixin, BaseAPIView):
    """Base view for admin-only endpoints"""
    required_roles = ['admin']

class AdminOrDeliveryView(RoleRequiredMixin, BaseAPIView):
    """Base view for admin or delivery partner endpoints"""
    required_roles = ['admin', 'delivery_partner']

class BookingRelatedView(BookingAccessMixin, BaseAPIView):
    """Base view for booking-related endpoints"""

    def get_booking(self, booking_id):
        """Get booking with access check"""
        return self.get_booking_or_403(booking_id, self.request.user)

# Reusable form validation functions
class FormValidators:
    """Reusable form validation functions"""

    @staticmethod
    def validate_booking_data(data):
        """Validate booking creation data"""
        errors = {}

        try:
            ValidationUtils.validate_address(data.get('pickup_address'), 'Pickup address')
        except Exception as e:
            errors['pickup_address'] = str(e)

        try:
            ValidationUtils.validate_address(data.get('delivery_address'), 'Delivery address')
        except Exception as e:
            errors['delivery_address'] = str(e)

        try:
            ValidationUtils.validate_mobile_number(data.get('customer_phone', ''))
        except Exception as e:
            errors['customer_phone'] = str(e)

        # Validate price
        try:
            price = float(data.get('estimated_price', 0))
            if price < 0:
                errors['estimated_price'] = "Price must be positive"
        except (ValueError, TypeError):
            errors['estimated_price'] = "Invalid price format"

        return errors

    @staticmethod
    def validate_status_update(data):
        """Validate status update data"""
        errors = {}

        valid_statuses = ['start', 'reached', 'collected', 'delivered']
        status = data.get('status')

        if not status:
            errors['status'] = "Status is required"
        elif status not in valid_statuses:
            errors['status'] = f"Status must be one of: {', '.join(valid_statuses)}"

        return errors

# Database query utilities
class QueryUtils:
    """Reusable database query utilities"""

    @staticmethod
    def get_user_bookings(user):
        """Get bookings based on user role"""
        from apps.booking.models import Booking

        if user.role == 'customer':
            return Booking.objects.filter(customer=user)
        elif user.role == 'delivery_partner':
            return Booking.objects.filter(delivery_partner=user)
        elif user.role == 'admin':
            return Booking.objects.all()
        else:
            return Booking.objects.none()

    @staticmethod
    def get_available_delivery_partners():
        """Get all available delivery partners"""
        return User.objects.filter(
            role='delivery_partner',
            is_active=True
        )

    @staticmethod
    def get_unassigned_bookings():
        """Get bookings without assigned delivery partners"""
        from apps.booking.models import Booking
        return Booking.objects.filter(
            delivery_partner__isnull=True,
            status='start'
        )

# Context processors for templates
def app_context(request):
    """Add common context data to all templates"""
    context = {
        'app_name': 'Food Delivery',
        'app_version': '1.0.0',
        'current_year': timezone.now().year,
        'timestamp': int(timezone.now().timestamp()),
    }

    if request.user.is_authenticated:
        context.update({
            'user_role': request.user.role,
            'user_display_name': request.user.mobile_number,
            'unread_messages_count': 0,  # Can be implemented later
        })

    return context
