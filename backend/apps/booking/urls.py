from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.BookingListView.as_view(), name='list'),
    path('create/', views.BookingCreateView.as_view(), name='create'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='detail'),
    path('<int:pk>/cancel/', views.BookingCancelView.as_view(), name='cancel'),
    path('<int:pk>/update-status/', views.BookingStatusUpdateView.as_view(), name='update_status'),
    path('assign/<int:pk>/', views.AssignBookingView.as_view(), name='assign'),
]
