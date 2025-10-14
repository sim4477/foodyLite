from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.booking.models import Booking

User = get_user_model()


class ChatRoom(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='chat_room')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat Room for Booking #{self.booking.id}"

    @property
    def participants(self):
        return [self.booking.customer, self.booking.delivery_partner]


class ChatMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.mobile_number}: {self.message[:50]}..."
