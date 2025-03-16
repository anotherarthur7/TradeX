from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponseRedirect
from .models import Offer
from .forms import OfferForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Thread, Message
from .forms import ThreadForm, MessageForm
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm

def is_admin(user):
    return user.is_staff

def thread_list(request):
    # Get all threads
    threads = Thread.objects.all()

    # Separate threads into categories
    open_threads = [thread for thread in threads if thread.offer and thread.offer.is_open]
    closed_threads = [thread for thread in threads if thread.offer and not thread.offer.is_open]
    technical_threads = [thread for thread in threads if not thread.offer]

    # Determine which threads to display based on the 'show_closed' and 'show_technical' parameters
    show_closed = request.GET.get('show_closed', 'false').lower() == 'true'
    show_technical = request.GET.get('show_technical', 'true').lower() == 'true'  # Default to True

    # Ensure only one of the parameters is active at a time
    if show_technical:
        displayed_threads = technical_threads
    elif show_closed:
        displayed_threads = closed_threads
    else:
        displayed_threads = open_threads

    return render(request, 'forum/thread_list.html', {
        'open_threads': open_threads,
        'closed_threads': closed_threads,
        'technical_threads': technical_threads,
        'displayed_threads': displayed_threads,
        'show_closed': show_closed,
        'show_technical': show_technical,
    })


def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    message_list = thread.messages.all()

    # Check if the thread is immutable (i.e., associated offer is closed)
    is_immutable = thread.offer and not thread.offer.is_open

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to post a message.")
            return redirect('login')

        # Prevent posting if the thread is immutable
        if is_immutable:
            messages.error(request, "This thread is closed and cannot be modified.")
            return redirect('thread_detail', thread_id=thread.id)

        # Prevent non-admin users from posting in technical threads
        if thread.is_technical and not request.user.is_staff:
            messages.error(request, "Only admin users can post messages in technical threads.")
            return redirect('thread_detail', thread_id=thread.id)

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
        'is_immutable': is_immutable,
    })

@staff_member_required
@login_required
def thread_create(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user

            # Ensure the offer is either open or null
            if thread.offer and not thread.offer.is_open:
                messages.error(request, "You cannot attach a thread to a closed offer.")
            else:
                # Save the thread if the offer is open or null
                thread.save()
                messages.success(request, "Thread created successfully!")
                return redirect('thread_list')
        else:
            # Handle form errors
            messages.error(request, "Please correct the errors below.")
    else:
        form = ThreadForm()
    return render(request, 'forum/thread_create.html', {'form': form})

@staff_member_required
@login_required
def thread_delete(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    if request.method == 'POST':
        thread.delete()
        return redirect('thread_list')
    return redirect('thread_detail', thread_id=thread.id)

@login_required
def message_delete(request, message_id):
    # Get the message or return a 404 error
    message = get_object_or_404(Message, id=message_id)

    # Ensure only admin users can delete messages
    if not request.user.is_staff:
        return redirect('forum/thread_detail', thread_id=message.thread.id)

    # Delete the message
    message.delete()

    # Redirect back to the thread detail page
    return redirect('forum/thread_detail', thread_id=message.thread.id)

def home(request):
    return render(request, 'home.html', {'is_home': True})

def about(request):
	return render(request, "about.html")

def offermain(request):
    show_closed = request.GET.get('show_closed', 'false').lower() == 'true'  # Convert to boolean
    if show_closed:
        offers = Offer.objects.filter(is_open=False)
    else:
        offers = Offer.objects.filter(is_open=True)
    return render(request, "offermain.html", {"offers": offers, "show_closed": show_closed})


def itemIndex(request, req_id):
    offer = get_object_or_404(Offer, id=req_id)
    is_admin = request.user.is_staff
    is_author = request.user == offer.user
    thread = offer.threads.first()  # Get the associated thread

    # Allow the author to close the offer
    if request.method == 'POST' and is_author:
        offer.is_open = False
        offer.save()
        messages.success(request, "The offer has been closed.")
        return redirect('item_index', req_id=req_id)

    return render(request, "offers.html", {
        "offer": offer,
        "is_admin": is_admin,
        "is_author": is_author,
        "thread": thread,  # Pass the thread to the template
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
    
    # Only the author can edit the offer
    if request.user != offer.user:
        messages.error(request, "You do not have permission to edit this offer.")
        return redirect('item_index', req_id=req_id)

    # Prevent editing if the offer is closed
    if not offer.is_open:
        messages.error(request, "This offer is closed and cannot be edited.")
        return redirect('item_index', req_id=req_id)

    if request.method == 'POST':
        form = OfferForm(request.POST, request.FILES, instance=offer)
        if form.is_valid():
            form.save()
            messages.success(request, "Offer updated successfully.")
            return redirect('item_index', req_id=req_id)
    else:
        form = OfferForm(instance=offer)

    return render(request, 'edit_offer.html', {'form': form, 'offer': offer})

@login_required
def delete_offer(request, req_id):
    offer = get_object_or_404(Offer, id=req_id)
    
    # Only the author or admin can delete the offer
    if not (request.user.is_staff or request.user == offer.user):
        messages.error(request, "You do not have permission to delete this offer.")
        return redirect('item_index', req_id=req_id)

    offer.delete()
    messages.success(request, "Offer deleted successfully.")
    return redirect('home')

@login_required
def profile(request):
    if request.method == 'POST':
        # Change password
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in
            messages.success(request, 'Password updated successfully.')
            return redirect('profile')  # Redirect to avoid resubmission
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        password_form = PasswordChangeForm(request.user)

    return render(request, 'profile.html', {
        'password_form': password_form,
    })

@login_required
def my_offers(request):
    open_offers = Offer.objects.filter(user=request.user, is_open=True)
    closed_offers = Offer.objects.filter(user=request.user, is_open=False)
    has_offers = open_offers.exists() or closed_offers.exists()  # Check if user has any offers

    return render(request, "my_offers.html", {
        "open_offers": open_offers,
        "closed_offers": closed_offers,
        "has_offers": has_offers,  # Pass the flag to the template
    })