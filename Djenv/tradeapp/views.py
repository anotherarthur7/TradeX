from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import HttpResponseRedirect
from .models import Offer
from .forms import OfferForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Thread, Message
from .forms import ThreadForm, MessageForm

def is_admin(user):
    return user.is_staff

def thread_list(request):
    threads = Thread.objects.all()
    return render(request, 'forum/thread_list.html', {'threads': threads})

def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    message_list = thread.messages.all()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Redirect unauthorized users to the login page
            messages.error(request, "You must be logged in to post a message.")
            return redirect('login')  # Replace 'login' with your login URL name

        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.author = request.user
            message.save()
            return redirect('thread_detail', thread_id=thread.id)
    else:
        form = MessageForm()

    return render(request, 'forum/thread_detail.html', {
        'thread': thread,
        'messages': message_list,
        'form': form,
    })

@user_passes_test(is_admin)
@login_required
def thread_create(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user
            thread.save()
            return redirect('thread_list')
    else:
        form = ThreadForm()
    return render(request, 'forum/thread_create.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)  # Only allow staff (admins) to delete threads
@login_required
def thread_delete(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    if request.method == 'POST':
        thread.delete()  # Delete the thread
        return redirect('thread_list')  # Redirect to the thread list after deletion
    return redirect('thread_detail', thread_id=thread.id)  # Fallback redirect

@login_required
def message_edit(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if request.user != message.author and not request.user.is_staff and request.user :
        return redirect('thread_detail', thread_id=message.thread.id)
    if request.method == 'POST':
        if 'delete' in request.POST:
            message.delete()
        else:
            form = MessageForm(request.POST, instance=message)
            if form.is_valid():
                form.save()
        return redirect('thread_detail', thread_id=message.thread.id)
    else:
        form = MessageForm(instance=message)
    return render(request, 'forum/message_edit.html', {'form': form, 'message': message})

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