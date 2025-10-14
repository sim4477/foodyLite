from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('room/<int:booking_id>/', views.ChatRoomView.as_view(), name='room'),
    path('api/messages/<int:booking_id>/', views.ChatMessagesAPIView.as_view(), name='messages_api'),
    path('api/send-message/', views.ChatMessagesAPIView.as_view(), name='send_message'),
]
