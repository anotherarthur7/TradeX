from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponseRedirect
from .models import Offer
from django.http import JsonResponse
from .forms import OfferForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Thread, Message
from .forms import ThreadForm, MessageForm
from django.utils import timezone
from .forms import CustomPasswordChangeForm
from django.core.mail import send_mail
from django.conf import settings
import json
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

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

@require_POST
def message_edit(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    # Check if the user is the author and the message is editable
    if request.user != message.author or not message.is_editable():
        return JsonResponse({'success': False, 'error': 'You cannot edit this message.'})

    # Update the message content
    form = MessageForm(request.POST, instance=message)
    if form.is_valid():
        form.save()
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
            }
        })
    else:
        return JsonResponse({'success': False, 'error': 'Invalid form submission.'})

def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    message_list = thread.messages.all()

    # Check if the thread is immutable (i.e., associated offer is closed)
    is_immutable = thread.offer and not thread.offer.is_open

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'You must be logged in to post a message.'})

        # Prevent posting if the thread is immutable
        if is_immutable:
            return JsonResponse({'success': False, 'error': 'This thread is closed and cannot be modified.'})

        # Prevent non-admin users from posting in technical threads
        if thread.is_technical and not request.user.is_staff:
            return JsonResponse({'success': False, 'error': 'Only admin users can post messages in technical threads.'})

        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.author = request.user
            message.save()

            # Return success response with message details
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'author': message.author.username,
                    'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid form submission.'})
    else:
        form = MessageForm()

    return render(request, 'forum/thread_detail.html', {
        'thread': thread,
        'messages': message_list,
        'form': form,
        'is_immutable': is_immutable,
    })


@login_required
def thread_create(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user

            # Ensure the offer is approved
            if thread.offer and thread.offer.status != 'approved':
                messages.error(request, "You cannot attach a thread to a non-approved offer.")
            else:
                # Save the thread if the offer is approved
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
    # Fetch the message or return a 404 error if it doesn't exist
    message = get_object_or_404(Message, id=message_id)

    # Ensure the user is an admin or the message author
    if request.user.is_staff or request.user == message.author:
        message.delete()
        messages.success(request, 'Message deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this message.')

    # Redirect back to the thread detail page
    return redirect('thread_detail', thread_id=message.thread.id)

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
            offer.status = 'pending'
            offer.save()
            messages.success(request, 'Your offer has been submitted and is pending approval.')
            return JsonResponse({'success': True})
        else:
            # Return form errors as JSON
            errors = {field: error.get_json_data() for field, error in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    else:
        form = OfferForm()
    return render(request, 'create.html', {'form': form})

def login_view(request):
    storage = messages.get_messages(request)
    for message in storage:
        pass 

    if request.user.is_authenticated:
        print("User logged in:", request.user.is_authenticated)
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me') == 'on'  # Check if "Remember Me" is selected

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Set a "Remember Me" cookie if selected
            if remember_me:
                response = JsonResponse({'success': True})
                response.set_cookie(
                    'remember_me',
                    json.dumps({'username': username, 'password': password}),
                    max_age=30 * 24 * 3600,  # Expires in 30 days
                    secure=True,  # Only send over HTTPS
                    httponly=True,  # Prevent JavaScript access
                    samesite='Lax'  # Prevent CSRF attacks
                )
                return response
            else:
                # Delete the "Remember Me" cookie if not selected
                response = JsonResponse({'success': True})
                response.delete_cookie('remember_me')
                return response
        else:
            return JsonResponse({'success': False, 'error': 'Invalid username or password.'})
    return render(request, 'login.html')

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
    return redirect('offermain')

@login_required
def profile(request):
    if request.method == 'POST':
        # Use the custom password change form
        password_form = CustomPasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in
            messages.success(request, 'Password updated successfully.')
            return redirect('profile')  # Redirect to avoid resubmission
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        password_form = CustomPasswordChangeForm(request.user)

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

@user_passes_test(lambda u: u.is_staff)
def review_offers(request):
    pending_offers = Offer.objects.filter(status='pending')
    return render(request, 'review_offers.html', {'pending_offers': pending_offers})

@staff_member_required
@require_POST
def approve_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    offer.status = 'approved'
    offer.is_open = True  # Mark the offer as open
    offer.save()

    # Notify the user via email
    send_mail(
        'Offer Approved',
        f'Your offer "{offer.title}" has been approved. A discussion thread has been created.',
        settings.DEFAULT_FROM_EMAIL,
        [offer.user.email],
        fail_silently=False,
    )

    return JsonResponse({'success': True})

@user_passes_test(lambda u: u.is_staff)
@require_POST
def reject_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    offer.status = 'rejected'  # Set status to 'rejected'
    offer.is_open = False  # Mark the offer as closed
    offer.save()

    # Notify the user via email
    send_mail(
        'Offer Rejected',
        f'Your offer "{offer.title}" has been rejected.',
        settings.DEFAULT_FROM_EMAIL,
        [offer.user.email],
        fail_silently=False,
    )

    return JsonResponse({'success': True})

@user_passes_test(lambda u: u.is_staff) 
def manage_users(request):
    users = User.objects.all()  # Get all users
    return render(request, 'manage_users.html', {'users': users})

@user_passes_test(lambda u: u.is_staff)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        # Handle form submission to update user details
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, f'User "{user.username}" updated successfully.')
        return redirect('manage_users')
    return render(request, 'edit_user.html', {'user': user})

@user_passes_test(lambda u: u.is_staff)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'User "{user.username}" deleted successfully.')
        return redirect('manage_users')
    return render(request, 'confirm_delete_user.html', {'user': user})