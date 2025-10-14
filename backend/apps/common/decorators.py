# Reusable decorators for views and functions

from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .utils import ResponseHandler, PermissionUtils
from .exceptions import ServiceError, AuthenticationError, PermissionError

def api_endpoint(allowed_methods=None, require_auth=True, allowed_roles=None):
    """
    Decorator to create API endpoints with common functionality

    Args:
        allowed_methods: List of allowed HTTP methods
        require_auth: Whether authentication is required
        allowed_roles: List of allowed user roles
    """
    if allowed_methods is None:
        allowed_methods = ['POST']

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                # Check HTTP method
                if request.method not in allowed_methods:
                    return ResponseHandler.error(
                        f"Method {request.method} not allowed", 
                        status=405
                    )

                # Check authentication
                if require_auth and not request.user.is_authenticated:
                    return ResponseHandler.error("Authentication required", status=401)

                # Check user roles
                if allowed_roles and require_auth:
                    if not PermissionUtils.check_user_role(request.user, allowed_roles):
                        return ResponseHandler.error("Insufficient permissions", status=403)

                # Call the view function
                return view_func(request, *args, **kwargs)

            except ServiceError as e:
                return ResponseHandler.error(e.message, e.errors, e.status_code)
            except Exception as e:
                return ResponseHandler.error(f"Internal server error: {str(e)}", status=500)

        # Apply Django decorators
        wrapper = csrf_exempt(wrapper)
        if allowed_methods:
            wrapper = require_http_methods(allowed_methods)(wrapper)
        if require_auth:
            wrapper = login_required(wrapper)

        return wrapper

    return decorator

def customer_required(view_func):
    """Decorator for customer-only endpoints"""
    return api_endpoint(allowed_roles=['customer'])(view_func)

def delivery_partner_required(view_func):
    """Decorator for delivery partner-only endpoints"""
    return api_endpoint(allowed_roles=['delivery_partner'])(view_func)

def admin_required(view_func):
    """Decorator for admin-only endpoints"""
    return api_endpoint(allowed_roles=['admin'])(view_func)

def booking_access_required(view_func):
    """Decorator to check booking access permissions"""
    @wraps(view_func)
    def wrapper(request, booking_id, *args, **kwargs):
        try:
            from apps.booking.models import Booking

            booking = Booking.objects.get(id=booking_id)

            if not PermissionUtils.check_booking_access(request.user, booking):
                return ResponseHandler.error("Access denied to this booking", status=403)

            # Add booking to kwargs for the view
            kwargs['booking'] = booking
            return view_func(request, booking_id, *args, **kwargs)

        except Booking.DoesNotExist:
            return ResponseHandler.error("Booking not found", status=404)
        except Exception as e:
            return ResponseHandler.error(str(e), status=500)

    return wrapper

def handle_service_errors(view_func):
    """Decorator to handle service layer errors"""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except ServiceError as e:
            return ResponseHandler.error(e.message, e.errors, e.status_code)
        except Exception as e:
            return ResponseHandler.error(f"Unexpected error: {str(e)}", status=500)

    return wrapper

def log_api_call(view_func):
    """Decorator to log API calls"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .utils import log_user_activity, get_client_ip

        # Log the API call
        if request.user.is_authenticated:
            log_user_activity(
                request.user, 
                f"API call: {request.method} {request.path}",
                f"IP: {get_client_ip(request)}"
            )

        return view_func(request, *args, **kwargs)

    return wrapper

def rate_limit(max_requests=60, window=60):
    """Simple rate limiting decorator (basic implementation)"""
    # This is a basic implementation - in production use Redis-based rate limiting
    request_counts = {}

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            import time
            from .utils import get_client_ip

            client_ip = get_client_ip(request)
            now = time.time()

            # Clean old entries
            cutoff = now - window
            request_counts[client_ip] = [
                timestamp for timestamp in request_counts.get(client_ip, [])
                if timestamp > cutoff
            ]

            # Check rate limit
            if len(request_counts[client_ip]) >= max_requests:
                return ResponseHandler.error(
                    "Rate limit exceeded. Try again later.", 
                    status=429
                )

            # Add current request
            request_counts[client_ip].append(now)

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
