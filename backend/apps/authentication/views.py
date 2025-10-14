# Refactored authentication views using reusable functions

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from apps.common.decorators import api_endpoint, handle_service_errors
from apps.common.services import AuthenticationService
from apps.common.utils import ResponseHandler, parse_json_safely

def login_page(request):
    """Display login page"""
    if request.user.is_authenticated:
        return redirect('authentication:dashboard')
    return render(request, 'login.html')

@api_endpoint(allowed_methods=['POST'], require_auth=False)
@handle_service_errors
def check_user(request):
    """Check if user exists and return appropriate response"""
    data = parse_json_safely(request)
    mobile_number = data.get('mobile_number')

    if not mobile_number:
        return ResponseHandler.error("Mobile number is required")

    # Check if user exists
    from apps.authentication.models import User
    try:
        user = User.objects.get(mobile_number=mobile_number)
        # User exists, send OTP directly
        result = AuthenticationService.send_otp(
            mobile_number=mobile_number,
            role=user.role
        )
        return ResponseHandler.success(
            message="OTP sent successfully",
            data={
                'user_exists': True,
                'user_role': user.role,
                'otp_sent': True,
                **result
            }
        )
    except User.DoesNotExist:
        # User doesn't exist, show role selection
        return ResponseHandler.success(
            message="User not found. Please select your role.",
            data={
                'user_exists': False,
                'requires_role_selection': True
            }
        )

@api_endpoint(allowed_methods=['POST'], require_auth=False)
@handle_service_errors
def send_otp(request):
    """Send OTP to mobile number"""
    data = parse_json_safely(request)

    result = AuthenticationService.send_otp(
        mobile_number=data.get('mobile_number'),
        role=data.get('role', 'customer')
    )

    return ResponseHandler.success(
        message="OTP sent successfully",
        data=result
    )

@api_endpoint(allowed_methods=['POST'], require_auth=False)
@handle_service_errors
def verify_otp(request):
    """Verify OTP and login user"""
    data = parse_json_safely(request)

    result = AuthenticationService.verify_otp_and_login(
        mobile_number=data.get('mobile_number'),
        otp_code=data.get('otp_code'),
        role=data.get('role', 'customer')
    )

    # Login user
    login(request, result['user'])

    return ResponseHandler.success(
        message="Login successful",
        data={
            'user': {
                'id': result['user'].id,
                'mobile_number': result['user'].mobile_number,
                'role': result['user'].role,
                'username': result['user'].username
            }
        }
    )

@login_required
def dashboard(request):
    """User dashboard"""
    from apps.common.mixins import QueryUtils

    # Get user-specific data
    bookings = QueryUtils.get_user_bookings(request.user)
    recent_bookings = bookings[:5]  # Get last 5 bookings

    context = {
        'user': request.user,
        'role': request.user.role,
        'recent_bookings': recent_bookings,
        'total_bookings': bookings.count()
    }
    return render(request, 'dashboard.html', context)

@login_required
def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('authentication:login')

@api_endpoint(allowed_methods=['GET'])
def user_profile(request):
    """Get user profile"""
    from apps.authentication.serializers import UserSerializer

    serializer = UserSerializer(request.user)
    return ResponseHandler.success(
        message="Profile retrieved successfully",
        data=serializer.data
    )
