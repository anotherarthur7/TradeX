from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponseRedirect
from .models import Offer
from .forms import OfferForm, EditOfferForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.

def home(request):
	return render(request, "home.html")

def about(request):
	return render(request, "about.html")

def offermain(request):
	offers = Offer.objects.all()
	return render(request, "offermain.html", {"offers" : offers})

def itemIndex(request, req_id):
	return render(request, "offers.html", {"offer" : Offer.objects.get(id=req_id)}) 

@login_required
def create(request):
    if request.method == 'POST':
        form = OfferForm(request.POST, request.FILES)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.user = request.user
            offer.save()
            return redirect('home')
    else:
        form = OfferForm()
    return render(request, 'create.html', {'form': form})

def login_view(request):

    if request.user.is_authenticated:
        print("User logged in:", request.user.is_authenticated)
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print("User authenticated successfully:", user.username)
            login(request, user)
            print("User logged in:", request.user.is_authenticated)
            return redirect('profile')
        else:
            print("Authentication failed for username:", username)
            messages.error(request, 'Invalid username or password.')
    else:
        print("GET request received")
        return render(request, 'login.html')
        

    return render(request, 'home.html')
@login_required
def profile(request):
    user = request.user
    return render(request, 'profile.html', {'user': user})
@login_required
def user_offers(request):
     offers = Offer.objects.filter(user=request.user)
     return render(request, 'user_offers.html', {"offers" : offers})
@login_required
def edit_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id, user=request.user)
    if request.method == 'POST':
        form = EditOfferForm(request.POST, request.FILES, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('user_offers')
    else:
        form = EditOfferForm(instance=offer)
    return render(request, 'edit_offer.html', {'form': form, 'offer': offer})
def logout_view(request):
    logout(request)
    return redirect('home')