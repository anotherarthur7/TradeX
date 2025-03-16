from django.shortcuts import render, redirect
from register.forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
def register(response):
    
    if response.user.is_authenticated:
        return redirect('home')
    
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            # Return form errors as JSON
            errors = {field: form.errors[field] for field in form.errors}
            return JsonResponse({'success': False, 'errors': errors})
    else:
        form = RegisterForm()
        
    return render(response, "register.html", {"form": form})


    