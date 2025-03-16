from django import forms
from django.forms import ModelForm
from .models import Offer
from .models import models 
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Thread, Message
from django.core.exceptions import ValidationError

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['topic', 'offer']

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