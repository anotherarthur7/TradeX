from django.shortcuts import render, HttpResponse, get_object_or_404
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
	offers = Offer.objects.all()
	return render(request, "offermain.html", {"offers" : offers})

def itemIndex(request, req_id):
    offer = get_object_or_404(Offer, id=req_id)
    is_admin = request.user.is_staff
    is_author = request.user == offer.user
    return render(request, "offers.html", {
        "offer": offer,
        "is_admin": is_admin,
        "is_author": is_author,
    })

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
            return redirect('home')
        else:
            print("Authentication failed for username:", username)
            messages.error(request, 'Invalid username or password.')
    else:
        print("GET request received")
        return render(request, 'login.html')
        

    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def edit_offer(request, req_id):
    offer = get_object_or_404(Offer, id=req_id)
    if not (request.user.is_staff or request.user == offer.user):
        return redirect('item_index', req_id=req_id)

    if request.method == 'POST':
        form = OfferForm(request.POST, request.FILES, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('item_index', req_id=req_id)
    else:
        form = OfferForm(instance=offer)

    return render(request, 'edit_offer.html', {'form': form, 'offer': offer})

@login_required
def delete_offer(request, req_id):
    offer = get_object_or_404(Offer, id=req_id)
    if not (request.user.is_staff or request.user == offer.user):
        return redirect('item_index', req_id=req_id)

    offer.delete()
    return redirect('home')