from django import forms
from .models import Booking
from django.contrib.auth import get_user_model

User = get_user_model()


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['food_items', 'pickup_address', 'delivery_address', 'phone_number', 'total_amount', 'special_instructions']
        widgets = {
            'food_items': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe the food items you want to order'}),
            'pickup_address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Restaurant pickup address'}),
            'delivery_address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Your delivery address'}),
            'special_instructions': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Any special instructions for the delivery'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['total_amount'].widget.attrs.update({'step': '0.01', 'min': '0'})


class BookingStatusForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow delivery partner status updates
        self.fields['status'].choices = [
            ('started', 'Started'),
            ('reached', 'Reached'),
            ('collected', 'Collected'),
            ('delivered', 'Delivered'),
        ]


class AssignBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['delivery_partner']
        widgets = {
            'delivery_partner': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delivery_partner'].queryset = User.objects.filter(role='delivery_partner')
        self.fields['delivery_partner'].empty_label = "Select a delivery partner"
