import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import ChatRoom, ChatMessage
from apps.booking.models import Booking

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.room_group_name = f'booking_{self.booking_id}'
        
        # Check if user has permission to access this chat
        if await self.check_permission():
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']
        
        # Save message to database
        await self.save_message(message, sender_id)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'sender_name': await self.get_sender_name(sender_id),
                'timestamp': await self.get_current_timestamp(),
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        sender_name = event['sender_name']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'sender_name': sender_name,
            'timestamp': timestamp,
        }))

    @database_sync_to_async
    def check_permission(self):
        """Check if user has permission to access this chat room"""
        try:
            booking = Booking.objects.get(id=self.booking_id)
            user = self.scope['user']
            
            if user.is_authenticated:
                # Check if user is either customer or assigned delivery partner
                return (user == booking.customer or 
                       (user == booking.delivery_partner and booking.delivery_partner))
            return False
        except Booking.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, message, sender_id):
        """Save message to database"""
        try:
            booking = Booking.objects.get(id=self.booking_id)
            chat_room, created = ChatRoom.objects.get_or_create(booking=booking)
            sender = User.objects.get(id=sender_id)
            
            ChatMessage.objects.create(
                chat_room=chat_room,
                sender=sender,
                message=message
            )
        except (Booking.DoesNotExist, User.DoesNotExist):
            pass

    @database_sync_to_async
    def get_sender_name(self, sender_id):
        """Get sender's display name"""
        try:
            user = User.objects.get(id=sender_id)
            return f"{user.get_role_display()} - {user.mobile_number}"
        except User.DoesNotExist:
            return "Unknown"

    @database_sync_to_async
    def get_current_timestamp(self):
        """Get current timestamp"""
        return timezone.now().isoformat()
