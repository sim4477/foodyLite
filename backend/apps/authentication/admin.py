from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, OTP

class CustomUserAdmin(UserAdmin):
    list_display = ('mobile_number', 'username', 'role', 'is_mobile_verified', 'is_active', 'created_at')
    list_filter = ('role', 'is_mobile_verified', 'is_active')
    search_fields = ('mobile_number', 'username')
    ordering = ('-created_at',)

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('mobile_number', 'role', 'is_mobile_verified')}),
    )

class OTPAdmin(admin.ModelAdmin):
    list_display = ('mobile_number', 'otp_code', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('mobile_number',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(OTP, OTPAdmin)
