from django.shortcuts import render, HttpResponse
from .models import Offer

# Create your views here.

def home(request):
	return render(request, "home.html")

def items(request):
	offers = Offer.objects.all() # retrieves ALL info about DB's Item object
	return render(request, "offers.html", {"offers" : offers})