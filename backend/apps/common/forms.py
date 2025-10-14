# Reusable form classes

from django import forms
from django.contrib.auth import get_user_model
from apps.common.utils import ValidationUtils
from apps.booking.models import Booking

User = get_user_model()

class BaseModelForm(forms.ModelForm):
    """Base form class with common functionality"""

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Add Bootstrap classes to all form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })

    def clean(self):
        """Common form validation"""
        cleaned_data = super().clean()

        # Add any common validation logic here
        return cleaned_data

class BookingForm(BaseModelForm):
    """Reusable booking form"""

    class Meta:
        model = Booking
        fields = [
            'pickup_address', 'delivery_address', 
            'customer_phone', 'delivery_notes', 'estimated_price'
        ]
        widgets = {
            'pickup_address': forms.Textarea(attrs={'rows': 3}),
            'delivery_address': forms.Textarea(attrs={'rows': 3}),
            'delivery_notes': forms.Textarea(attrs={'rows': 2}),
            'estimated_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
        }

    def clean_customer_phone(self):
        """Validate customer phone number"""
        phone = self.cleaned_data['customer_phone']
        try:
            return ValidationUtils.validate_mobile_number(phone)
        except Exception as e:
            raise forms.ValidationError(str(e))

    def clean_pickup_address(self):
        """Validate pickup address"""
        address = self.cleaned_data['pickup_address']
        try:
            return ValidationUtils.validate_address(address, 'Pickup address')
        except Exception as e:
            raise forms.ValidationError(str(e))

    def clean_delivery_address(self):
        """Validate delivery address"""
        address = self.cleaned_data['delivery_address']
        try:
            return ValidationUtils.validate_address(address, 'Delivery address')
        except Exception as e:
            raise forms.ValidationError(str(e))

    def clean_estimated_price(self):
        """Validate estimated price"""
        price = self.cleaned_data['estimated_price']
        if price and price < 0:
            raise forms.ValidationError("Price must be positive")
        return price

class OTPVerificationForm(forms.Form):
    """Reusable OTP verification form"""

    mobile_number = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 10-digit mobile number',
            'pattern': '[0-9]{10}',
            'maxlength': '10'
        })
    )

    role = forms.ChoiceField(
        choices=[
            ('customer', 'Customer'),
            ('delivery_partner', 'Delivery Partner'),
            ('admin', 'Admin')
        ],
        initial='customer'
    )

    def clean_mobile_number(self):
        """Validate mobile number"""
        mobile = self.cleaned_data['mobile_number']
        try:
            return ValidationUtils.validate_mobile_number(mobile)
        except Exception as e:
            raise forms.ValidationError(str(e))

class StatusUpdateForm(forms.Form):
    """Reusable status update form"""

    STATUS_CHOICES = [
        ('start', 'Started'),
        ('reached', 'Reached'),
        ('collected', 'Collected'),
        ('delivered', 'Delivered')
    ]

    status = forms.ChoiceField(choices=STATUS_CHOICES)
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional notes'})
    )

    def __init__(self, current_status=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit choices based on current status
        if current_status:
            valid_next_statuses = {
                'start': ['reached'],
                'reached': ['collected'],
                'collected': ['delivered']
            }

            next_statuses = valid_next_statuses.get(current_status, [])
            if next_statuses:
                choices = [(status, dict(self.STATUS_CHOICES)[status]) 
                          for status in next_statuses]
                self.fields['status'].choices = choices

class ChatMessageForm(forms.Form):
    """Reusable chat message form"""

    message = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': 'Type your message...',
            'maxlength': '1000'
        })
    )

    def clean_message(self):
        """Validate message"""
        message = self.cleaned_data['message'].strip()
        if not message:
            raise forms.ValidationError("Message cannot be empty")
        return message
