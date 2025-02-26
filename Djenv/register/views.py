from django.shortcuts import render, redirect
from register.forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

# Create your views here.
def register(response):
    if response.user.is_authenticated:
        return redirect('home')
    
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
            messages.success(response, 'Registration successful! Please log in.')
            return redirect('login')  # Redirect to the login page after registration
    else:
        form = RegisterForm()
        
        
    return render(response, "register.html", {"form":form})


    