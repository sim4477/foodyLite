from django.contrib import admin
from .models import ChatRoom, ChatMessage


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'created_at']
    list_filter = ['created_at']
    search_fields = ['booking__customer__mobile_number']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat_room', 'sender', 'message_preview', 'created_at', 'is_read']
    list_filter = ['created_at', 'is_read']
    search_fields = ['message', 'sender__mobile_number']
    readonly_fields = ['created_at']

    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'
