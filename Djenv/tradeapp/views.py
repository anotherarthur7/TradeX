from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponseRedirect
from .models import Offer
from .forms import OfferForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.

def home(request):
	return render(request, "home.html")

def about(request):
	return render(request, "about.html")

def offermain(request):
	offers = Offer.objects.all() # retrieves ALL info about DB's Item object
	return render(request, "offermain.html", {"offers" : offers})

def itemIndex(request, req_id):
	return render(request, "offers.html", {"offer" : Offer.objects.get(id=req_id)}) 

@login_required
def create(request):
    if request.method == 'POST':
        form = OfferForm(request.POST, request.FILES)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.user = request.user  # Associate the offer with the logged-in user
            offer.save()
            return redirect('home')  # Redirect to the homepage after creation
    else:
        form = OfferForm()
    return render(request, 'create.html', {'form': form})

def login_view(request):

    if request.user.is_authenticated:
        print("User logged in:", request.user.is_authenticated)  # Debugging
        return redirect('home')  # Redirect logged-in users to the homepage
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print("User authenticated successfully:", user.username)  # Debugging
            login(request, user)
            print("User logged in:", request.user.is_authenticated)  # Debugging
            return redirect('home')  # Redirect to the homepage after login
        else:
            print("Authentication failed for username:", username)  # Debugging
            messages.error(request, 'Invalid username or password.')
    else:
        print("GET request received")  # Debugging
        return render(request, 'login.html')  # Render the login page for GET requests
        

    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to the homepage after logout