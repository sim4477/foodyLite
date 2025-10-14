from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('started', 'Started'),
        ('reached', 'Reached'),
        ('collected', 'Collected'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_bookings')
    delivery_partner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_bookings')
    food_items = models.TextField(help_text="Description of food items ordered")
    pickup_address = models.TextField()
    delivery_address = models.TextField()
    phone_number = models.CharField(max_length=15)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_bookings')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.id} - {self.customer.mobile_number}"

    @property
    def can_be_cancelled(self):
        return self.status in ['pending', 'assigned']

    @property
    def can_chat(self):
        return self.status in ['assigned', 'started', 'reached', 'collected']
