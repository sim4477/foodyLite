from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.booking.models import Booking
from apps.chat.models import ChatRoom
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test users and sample data for the food delivery app'

    def handle(self, *args, **options):
        self.stdout.write('Creating test users and sample data...')

        # Create test users
        users_data = [
            {'mobile_number': '9999999999', 'role': 'customer', 'username': 'customer1'},
            {'mobile_number': '8888888888', 'role': 'customer', 'username': 'customer2'},
            {'mobile_number': '7777777777', 'role': 'delivery_partner', 'username': 'delivery1'},
            {'mobile_number': '6666666666', 'role': 'delivery_partner', 'username': 'delivery2'},
            {'mobile_number': '5555555555', 'role': 'admin', 'username': 'admin1'},
        ]

        created_users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                mobile_number=user_data['mobile_number'],
                defaults={
                    'username': user_data['username'],
                    'role': user_data['role'],
                    'is_mobile_verified': True,
                    'first_name': f"Test {user_data['role'].title()}",
                }
            )
            created_users.append(user)
            if created:
                self.stdout.write(f'Created {user_data["role"]}: {user_data["mobile_number"]}')

        # Create sample bookings
        booking_data = [
            {
                'food_items': 'Pizza Margherita, Garlic Bread, Coke',
                'pickup_address': 'Pizza Palace, MG Road, Bangalore',
                'delivery_address': '123 Main Street, Koramangala, Bangalore',
                'phone_number': '9999999999',
                'total_amount': 450.00,
                'special_instructions': 'Please ring the doorbell twice',
                'customer': created_users[0],
            },
            {
                'food_items': 'Chicken Biryani, Raita, Pickle',
                'pickup_address': 'Spice Garden, Brigade Road, Bangalore',
                'delivery_address': '456 Park Avenue, Indiranagar, Bangalore',
                'phone_number': '8888888888',
                'total_amount': 320.00,
                'special_instructions': 'Extra spicy please',
                'customer': created_users[1],
            },
            {
                'food_items': 'Veg Thali, Dal, Rice, Roti',
                'pickup_address': 'Taste of India, Commercial Street, Bangalore',
                'delivery_address': '789 Garden Street, Whitefield, Bangalore',
                'phone_number': '9999999999',
                'total_amount': 180.00,
                'customer': created_users[0],
            },
        ]

        for booking_info in booking_data:
            booking, created = Booking.objects.get_or_create(
                customer=booking_info['customer'],
                food_items=booking_info['food_items'],
                defaults=booking_info
            )
            if created:
                self.stdout.write(f'Created booking: {booking.id}')

        # Assign some bookings to delivery partners
        bookings = Booking.objects.filter(status='pending')
        delivery_partners = User.objects.filter(role='delivery_partner')

        if bookings.exists() and delivery_partners.exists():
            # Assign first booking to first delivery partner
            first_booking = bookings.first()
            first_partner = delivery_partners.first()
            
            first_booking.delivery_partner = first_partner
            first_booking.status = 'assigned'
            first_booking.save()
            
            self.stdout.write(f'Assigned booking {first_booking.id} to delivery partner {first_partner.mobile_number}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created test data!')
        )
        self.stdout.write('\nTest Users:')
        self.stdout.write('- Customer: 9999999999 (password: not needed, use OTP: 1234)')
        self.stdout.write('- Customer: 8888888888 (password: not needed, use OTP: 1234)')
        self.stdout.write('- Delivery Partner: 7777777777 (password: not needed, use OTP: 1234)')
        self.stdout.write('- Delivery Partner: 6666666666 (password: not needed, use OTP: 1234)')
        self.stdout.write('- Admin: 5555555555 (password: not needed, use OTP: 1234)')
        self.stdout.write('\nNote: Use OTP "1234" for all test users')
