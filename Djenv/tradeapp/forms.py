from django import forms
from .models import Offer
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from .models import Thread, Message, Report
from django.core.exceptions import ValidationError

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['topic', 'offer', 'is_technical']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter offers to only show approved ones
        self.fields['offer'].queryset = Offer.objects.filter(status='approved')
        
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']

class OfferForm(forms.ModelForm):
    title = forms.CharField(
        label="Offer Title",
        widget=forms.TextInput(attrs={'class': 'custom-form-control', 'placeholder': 'Enter title'})
    )
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(attrs={'class': 'custom-form-control', 'placeholder': 'Enter description', 'rows': 4})
    )
    price = forms.DecimalField(
        label="Price",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'custom-form-control', 'placeholder': 'Enter price'})
    )
    image = forms.ImageField(
        label="Image",
        widget=forms.FileInput(attrs={'class': 'custom-form-control'})
    )

    class Meta:
        model = Offer
        fields = ['title', 'description', 'price', 'image']

    def clean_price(self):
        # Get the price value from the form data
        price = self.cleaned_data.get('price')

        # Check if the price is negative
        if price is not None and price < 0:
            raise ValidationError("Price cannot be negative. Please enter a valid price.")

        # Return the cleaned price
        return price
    
class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        old_password = self.cleaned_data.get('old_password')
        new_password1 = self.cleaned_data.get('new_password1')

        # Check if the new password is the same as the old password
        if old_password and new_password1 and old_password == new_password1:
            raise ValidationError("Your new password cannot be the same as your old password.")

        return new_password1
    
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'message']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }