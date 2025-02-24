from django import forms
from django.forms import ModelForm
from .models import Offer

class OfferForm(ModelForm):
    title = forms.TextInput()
    description = forms.TextInput()
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    image = forms.ImageField()
    class Meta:
        model = Offer
        fields = ['title', 'description', 'price', 'image']