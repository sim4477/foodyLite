# Service layer with reusable business logic

from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .utils import OTPHandler, ValidationUtils, log_user_activity
from .exceptions import ServiceError

User = get_user_model()
channel_layer = get_channel_layer()

class AuthenticationService:
    """Reusable authentication service"""

    @staticmethod
    def send_otp(mobile_number, role='customer'):
        """Send OTP to mobile number"""
        try:
            # Validate mobile number
            clean_mobile = ValidationUtils.validate_mobile_number(mobile_number)

            # Generate OTP (static as per requirements)
            otp_code = '1234'

            # Save OTP to database
            from apps.authentication.models import OTP
            otp_obj = OTP.objects.create(
                mobile_number=clean_mobile,
                otp_code=otp_code
            )

            # Send OTP via SMS (mock implementation)
            OTPHandler.send_otp_sms(clean_mobile, otp_code)

            log_user_activity(
                type('MockUser', (), {'mobile_number': clean_mobile, 'role': role})(), 
                f"OTP sent for {role} role"
            )

            # Return OTP for demo purposes (remove in production)
            return {
                'success': True,
                'otp': otp_code,  # Remove in production
                'mobile_number': clean_mobile
            }

        except Exception as e:
            raise ServiceError(f"Failed to send OTP: {str(e)}")

    @staticmethod
    def verify_otp_and_login(mobile_number, otp_code, role='customer'):
        """Verify OTP and create/login user"""
        try:
            # Validate inputs
            clean_mobile = ValidationUtils.validate_mobile_number(mobile_number)
            clean_otp = ValidationUtils.validate_otp(otp_code)

            # Verify static OTP
            if clean_otp != '1234':
                raise ServiceError("Invalid OTP")

            # Create OTP record for tracking
            from apps.authentication.models import OTP
            OTP.objects.create(
                mobile_number=clean_mobile,
                otp_code=clean_otp,
                is_verified=True
            )

            # Get or create user
            user, created = User.objects.get_or_create(
                mobile_number=clean_mobile,
                defaults={
                    'username': clean_mobile,
                    'role': role,
                    'is_mobile_verified': True
                }
            )

            if not created and not user.is_mobile_verified:
                user.is_mobile_verified = True
                user.save()

            log_user_activity(user, "Successful login")

            return {
                'success': True,
                'user': user,
                'created': created
            }

        except Exception as e:
            if isinstance(e, ServiceError):
                raise
            raise ServiceError(f"Login failed: {str(e)}")

class BookingService:
    """Reusable booking service"""

    @staticmethod
    @transaction.atomic
    def create_booking(customer, booking_data):
        """Create a new booking"""
        try:
            # Validate booking data
            from .mixins import FormValidators
            errors = FormValidators.validate_booking_data(booking_data)
            if errors:
                raise ServiceError("Validation failed", errors)

            # Create booking
            from apps.booking.models import Booking, BookingStatusHistory
            booking = Booking.objects.create(
                customer=customer,
                pickup_address=booking_data['pickup_address'],
                delivery_address=booking_data['delivery_address'],
                customer_phone=booking_data.get('customer_phone', customer.mobile_number),
                delivery_notes=booking_data.get('delivery_notes', ''),
                estimated_price=booking_data.get('estimated_price', 50.00)
            )

            # Create status history
            BookingStatusHistory.objects.create(
                booking=booking,
                status='start',
                updated_by=customer,
                notes='Booking created'
            )

            log_user_activity(customer, f"Created booking #{booking.id}")

            # Notify admins about new booking
            BookingService.notify_new_booking(booking)

            return {
                'success': True,
                'booking': booking
            }

        except Exception as e:
            if isinstance(e, ServiceError):
                raise
            raise ServiceError(f"Failed to create booking: {str(e)}")

    @staticmethod
    @transaction.atomic
    def assign_booking(booking_id, delivery_partner_id, admin_user):
        """Assign booking to delivery partner"""
        try:
            from apps.booking.models import Booking, BookingStatusHistory

            booking = Booking.objects.get(id=booking_id)
            delivery_partner = User.objects.get(
                id=delivery_partner_id, 
                role='delivery_partner'
            )

            # Assign delivery partner
            booking.delivery_partner = delivery_partner
            booking.assigned_at = timezone.now()
            booking.save()

            # Create status history
            BookingStatusHistory.objects.create(
                booking=booking,
                status='assigned',
                updated_by=admin_user,
                notes=f'Assigned to {delivery_partner.mobile_number}'
            )

            # Send real-time notification
            BookingService.notify_booking_update(booking, {
                'type': 'assignment',
                'message': f'Booking assigned to {delivery_partner.mobile_number}',
                'assigned_to': delivery_partner.mobile_number
            })

            log_user_activity(admin_user, f"Assigned booking #{booking.id} to {delivery_partner.mobile_number}")

            return {
                'success': True,
                'booking': booking,
                'delivery_partner': delivery_partner
            }

        except Exception as e:
            raise ServiceError(f"Failed to assign booking: {str(e)}")

    @staticmethod
    @transaction.atomic
    def update_booking_status(booking_id, new_status, user, notes=''):
        """Update booking status"""
        try:
            from apps.booking.models import Booking, BookingStatusHistory

            booking = Booking.objects.get(id=booking_id)

            # Validate status transition
            valid_transitions = {
                'start': ['reached'],
                'reached': ['collected'], 
                'collected': ['delivered']
            }

            current_status = booking.status
            if (current_status in valid_transitions and 
                new_status not in valid_transitions[current_status] and 
                user.role != 'admin'):
                raise ServiceError(f"Invalid status transition from {current_status} to {new_status}")

            # Update booking status
            booking.update_status(new_status)

            # Create status history
            BookingStatusHistory.objects.create(
                booking=booking,
                status=new_status,
                updated_by=user,
                notes=notes
            )

            # Send real-time notification
            BookingService.notify_booking_update(booking, {
                'type': 'status_update',
                'status': new_status,
                'updated_by': user.mobile_number,
                'notes': notes,
                'timestamp': timezone.now().isoformat()
            })

            log_user_activity(user, f"Updated booking #{booking.id} status to {new_status}")

            return {
                'success': True,
                'booking': booking,
                'new_status': new_status
            }

        except Exception as e:
            if isinstance(e, ServiceError):
                raise
            raise ServiceError(f"Failed to update status: {str(e)}")

    @staticmethod
    def notify_booking_update(booking, data):
        """Send real-time notification for booking update"""
        try:
            async_to_sync(channel_layer.group_send)(
                f'booking_{booking.id}',
                {
                    'type': 'booking_update',
                    'message': {
                        'booking_id': booking.id,
                        **data
                    }
                }
            )
        except Exception as e:
            print(f"Failed to send real-time notification: {e}")

    @staticmethod
    def notify_new_booking(booking):
        """Notify admins about new booking"""
        try:
            async_to_sync(channel_layer.group_send)(
                'admin_notifications',
                {
                    'type': 'new_booking',
                    'message': {
                        'booking_id': booking.id,
                        'customer': booking.customer.mobile_number,
                        'pickup_address': booking.pickup_address[:50] + '...'
                    }
                }
            )
        except Exception as e:
            print(f"Failed to send new booking notification: {e}")

class ChatService:
    """Reusable chat service"""

    @staticmethod
    def create_or_get_chat_room(booking):
        """Create or get chat room for booking"""
        from apps.chat.models import ChatRoom

        chat_room, created = ChatRoom.objects.get_or_create(
            booking=booking
        )
        return chat_room

    @staticmethod
    def save_message(booking_id, sender, message):
        """Save chat message to database"""
        try:
            from apps.booking.models import Booking
            from apps.chat.models import ChatMessage

            booking = Booking.objects.get(id=booking_id)
            chat_room = ChatService.create_or_get_chat_room(booking)

            chat_message = ChatMessage.objects.create(
                room=chat_room,
                sender=sender,
                message=message
            )

            log_user_activity(sender, f"Sent message in booking #{booking_id}")

            return chat_message

        except Exception as e:
            raise ServiceError(f"Failed to save message: {str(e)}")

    @staticmethod
    def get_chat_messages(booking_id, user):
        """Get chat messages for booking"""
        try:
            from apps.booking.models import Booking
            from apps.chat.models import ChatMessage
            from .utils import PermissionUtils

            booking = Booking.objects.get(id=booking_id)

            # Check permissions
            if not PermissionUtils.check_booking_access(user, booking):
                raise ServiceError("Access denied")

            chat_room = ChatService.create_or_get_chat_room(booking)
            messages = ChatMessage.objects.filter(room=chat_room)

            return messages

        except Exception as e:
            if isinstance(e, ServiceError):
                raise
            raise ServiceError(f"Failed to get messages: {str(e)}")
