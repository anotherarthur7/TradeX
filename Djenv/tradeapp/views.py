from django.shortcuts import render, HttpResponse
from django.shortcuts import HttpResponseRedirect
from .models import Offer
from .forms import OfferForm

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

def create(request):

	if request.method == "POST":
		form = OfferForm(request.POST, request.FILES)
		print(request.FILES)

		if form.is_valid():
			form.save()
		return HttpResponseRedirect("offermain")
		
	else:
		form = OfferForm()
		
	return render(request, "create.html", {"form": OfferForm})

#form.as_ul