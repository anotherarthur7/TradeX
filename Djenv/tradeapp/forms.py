from django import forms
from django.forms import ModelForm
from .models import Offer

class OfferForm(ModelForm):
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