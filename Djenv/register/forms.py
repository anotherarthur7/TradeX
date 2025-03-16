from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex='^[a-zA-Zа-яА-Я0-9_]+$',  # Allows letters (English and Russian), numbers, and underscores
                message='Username can only contain letters (English or Russian), numbers, and underscores.',
                code='invalid_username'
            )
        ]
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email
