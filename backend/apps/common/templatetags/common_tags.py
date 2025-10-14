# Custom template tags and filters for reusability

from django import template
from django.utils import timezone
from apps.common.utils import DateTimeUtils

register = template.Library()

@register.filter
def format_datetime(value, format_type='display'):
    """Format datetime using reusable utility"""
    return DateTimeUtils.format_datetime(value, format_type)

@register.filter
def time_since(value):
    """Get time difference from now"""
    if not value:
        return ""
    return DateTimeUtils.get_time_difference(value)

@register.filter
def status_badge_class(status):
    """Get Bootstrap class for status badge"""
    status_classes = {
        'start': 'bg-secondary',
        'reached': 'bg-warning',
        'collected': 'bg-info', 
        'delivered': 'bg-success',
        'assigned': 'bg-primary'
    }
    return status_classes.get(status, 'bg-secondary')

@register.filter
def user_role_icon(role):
    """Get icon for user role"""
    role_icons = {
        'customer': '👤',
        'delivery_partner': '🚚',
        'admin': '👨‍💼'
    }
    return role_icons.get(role, '👤')

@register.filter
def truncate_address(address, length=50):
    """Truncate address to specified length"""
    if not address:
        return ""

    if len(address) <= length:
        return address

    return address[:length] + "..."

@register.filter
def currency_format(amount):
    """Format currency amount"""
    try:
        return f"₹{float(amount):.2f}"
    except (ValueError, TypeError):
        return "₹0.00"

@register.simple_tag
def booking_progress_percentage(booking):
    """Calculate booking progress percentage"""
    status_progress = {
        'start': 25,
        'reached': 50,
        'collected': 75,
        'delivered': 100
    }
    return status_progress.get(booking.status, 0)

@register.inclusion_tag('components/status_badge.html')
def status_badge(status):
    """Render status badge component"""
    return {
        'status': status,
        'badge_class': status_badge_class(status),
        'status_display': status.replace('_', ' ').title()
    }

@register.inclusion_tag('components/user_avatar.html')
def user_avatar(user, size='sm'):
    """Render user avatar component"""
    return {
        'user': user,
        'size': size,
        'icon': user_role_icon(user.role if hasattr(user, 'role') else 'customer')
    }

@register.inclusion_tag('components/booking_card.html')
def booking_card(booking, user):
    """Render booking card component"""
    from apps.common.utils import PermissionUtils

    return {
        'booking': booking,
        'user': user,
        'can_edit': PermissionUtils.check_booking_access(user, booking),
        'progress': booking_progress_percentage(booking)
    }

@register.simple_tag(takes_context=True)
def user_can_edit_booking(context, booking):
    """Check if current user can edit booking"""
    user = context['user']
    if not user.is_authenticated:
        return False

    from apps.common.utils import PermissionUtils
    return PermissionUtils.check_booking_access(user, booking)

@register.simple_tag
def get_unread_messages_count(user, booking=None):
    """Get unread messages count for user"""
    try:
        from apps.chat.models import ChatMessage

        query = ChatMessage.objects.filter(is_read=False)

        if booking:
            query = query.filter(room__booking=booking)

        # Don't count user's own messages
        query = query.exclude(sender=user)

        return query.count()
    except:
        return 0

@register.filter
def json_encode(value):
    """Safely encode value as JSON for JavaScript"""
    import json
    from django.utils.safestring import mark_safe

    try:
        return mark_safe(json.dumps(value))
    except:
        return mark_safe('null')
