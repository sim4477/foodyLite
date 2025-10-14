from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Booking
from .forms import BookingForm, BookingStatusForm, AssignBookingForm


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'booking/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return Booking.objects.filter(customer=user)
        elif user.role == 'delivery_partner':
            return Booking.objects.filter(delivery_partner=user)
        elif user.role == 'admin':
            return Booking.objects.all()
        return Booking.objects.none()


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'booking/booking_form.html'
    success_url = reverse_lazy('booking:list')

    def form_valid(self, form):
        form.instance.customer = self.request.user
        messages.success(self.request, 'Booking created successfully!')
        return super().form_valid(form)


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'booking/booking_detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return Booking.objects.filter(customer=user)
        elif user.role == 'delivery_partner':
            return Booking.objects.filter(delivery_partner=user)
        elif user.role == 'admin':
            return Booking.objects.all()
        return Booking.objects.none()


class BookingCancelView(LoginRequiredMixin, UpdateView):
    model = Booking
    fields = []
    template_name = 'booking/booking_confirm_cancel.html'
    success_url = reverse_lazy('booking:list')

    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return Booking.objects.filter(customer=user)
        return Booking.objects.none()

    def post(self, request, *args, **kwargs):
        booking = self.get_object()
        if booking.can_be_cancelled:
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.cancelled_by = request.user
            booking.save()
            messages.success(request, 'Booking cancelled successfully!')
            return redirect('booking:list')
        messages.error(request, 'Cannot cancel this booking!')
        return redirect('booking:detail', pk=booking.pk)


class BookingStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    form_class = BookingStatusForm
    template_name = 'booking/booking_status_update.html'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'delivery_partner':
            return Booking.objects.filter(delivery_partner=user)
        return Booking.objects.none()

    def form_valid(self, form):
        messages.success(self.request, 'Status updated successfully!')
        return super().form_valid(form)


class AssignBookingView(LoginRequiredMixin, UpdateView):
    model = Booking
    form_class = AssignBookingForm
    template_name = 'booking/assign_booking.html'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Booking.objects.filter(status='pending')
        return Booking.objects.none()

    def form_valid(self, form):
        booking = form.save(commit=False)
        booking.status = 'assigned'
        booking.assigned_at = timezone.now()
        booking.save()
        messages.success(self.request, 'Booking assigned successfully!')
        return redirect('booking:detail', pk=booking.pk)
