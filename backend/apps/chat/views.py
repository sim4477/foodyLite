import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import ChatRoom, ChatMessage
from apps.booking.models import Booking


class ChatRoomView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/chat_room.html'

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        
        # Check permissions
        if not (request.user == booking.customer or 
                (request.user == booking.delivery_partner and booking.delivery_partner)):
            messages.error(request, 'You do not have permission to access this chat room.')
            return redirect('booking:detail', pk=booking_id)
        
        # Get or create chat room
        chat_room, created = ChatRoom.objects.get_or_create(booking=booking)
        
        context = {
            'booking': booking,
            'chat_room': chat_room,
            'user_role': request.user.role,
        }
        return render(request, self.template_name, context)


@method_decorator(csrf_exempt, name='dispatch')
class ChatMessagesAPIView(LoginRequiredMixin, TemplateView):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        
        # Check permissions
        if not (request.user == booking.customer or 
                (request.user == booking.delivery_partner and booking.delivery_partner)):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        try:
            chat_room = ChatRoom.objects.get(booking=booking)
            messages = ChatMessage.objects.filter(chat_room=chat_room).order_by('created_at')
            
            messages_data = []
            for message in messages:
                messages_data.append({
                    'id': message.id,
                    'message': message.message,
                    'sender_id': message.sender.id,
                    'sender_name': f"{message.sender.get_role_display()} - {message.sender.mobile_number}",
                    'timestamp': message.created_at.isoformat(),
                    'is_read': message.is_read,
                })
            
            return JsonResponse({'messages': messages_data})
        except ChatRoom.DoesNotExist:
            return JsonResponse({'messages': []})

    @method_decorator(csrf_exempt, name='dispatch')
    def post(self, request, booking_id):
        """Send a new message"""
        booking = get_object_or_404(Booking, id=booking_id)
        
        # Check permissions
        if not (request.user == booking.customer or 
                (request.user == booking.delivery_partner and booking.delivery_partner)):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            message_text = data.get('message', '').strip()
            
            if not message_text:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
            # Get or create chat room
            chat_room, created = ChatRoom.objects.get_or_create(booking=booking)
            
            # Create message
            chat_message = ChatMessage.objects.create(
                chat_room=chat_room,
                sender=request.user,
                message=message_text
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Message sent successfully',
                'message_id': chat_message.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
