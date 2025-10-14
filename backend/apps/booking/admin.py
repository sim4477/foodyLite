from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'delivery_partner', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__mobile_number', 'delivery_partner__mobile_number', 'food_items']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['customer', 'delivery_partner']
