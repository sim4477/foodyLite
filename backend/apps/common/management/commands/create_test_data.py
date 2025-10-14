# management/commands/create_test_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.booking.models import Booking, BookingStatusHistory
from apps.authentication.models import OTP
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test data for development'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of test users')
        parser.add_argument('--bookings', type=int, default=20, help='Number of test bookings')
        parser.add_argument('--clear', action='store_true', help='Clear existing test data first')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing test data...')
            self.clear_test_data()

        self.stdout.write('Creating test users...')
        users = self.create_test_users(options['users'])

        self.stdout.write('Creating test bookings...')
        self.create_test_bookings(users, options['bookings'])

        self.stdout.write(self.style.SUCCESS('Successfully created test data!'))

    def clear_test_data(self):
        User.objects.filter(mobile_number__startswith='test').delete()
        OTP.objects.filter(mobile_number__startswith='test').delete()

    def create_test_users(self, count):
        users = {'customers': [], 'delivery_partners': [], 'admins': []}

        for i in range(count):
            role = 'customer' if i < count * 0.6 else ('delivery_partner' if i < count * 0.9 else 'admin')
            mobile = f"test{i:06d}"

            user, created = User.objects.get_or_create(
                mobile_number=mobile,
                defaults={
                    'username': f"{role}_{i}",
                    'role': role,
                    'is_mobile_verified': True,
                    'is_active': True
                }
            )

            users[f"{role}s"].append(user)

            if created:
                self.stdout.write(f'Created {role}: {mobile}')

        return users

    def create_test_bookings(self, users, count):
        customers = users['customers']
        if not customers:
            return

        addresses = [
            'MG Road, Bangalore, Karnataka',
            'Connaught Place, New Delhi',
            'Marine Drive, Mumbai, Maharashtra'
        ]

        for i in range(count):
            customer = random.choice(customers)
            booking = Booking.objects.create(
                customer=customer,
                pickup_address=random.choice(addresses),
                delivery_address=random.choice(addresses),
                customer_phone=customer.mobile_number,
                estimated_price=random.uniform(50, 500)
            )

            self.stdout.write(f'Created booking #{booking.id}')
