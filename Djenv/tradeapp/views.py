from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponseRedirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Offer
from django.http import JsonResponse
from .forms import OfferForm, ReportForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Thread, Message, Report
from .forms import ThreadForm, MessageForm
from django.utils import timezone
from .forms import CustomPasswordChangeForm
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
from .models import VerificationCode
import json
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
import secrets
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from register import views as d
from django.shortcuts import render, redirect
from register.forms import RegisterForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import VerificationCode
from django.contrib.auth import login
from django_ratelimit.decorators import ratelimit

def is_admin(user):
    return user.is_staff

@ratelimit(key='ip', rate='10/m')
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

@login_required
@ratelimit(key='ip', rate='3/m')
def message_create(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    # Check if the user is allowed to post messages
    if not request.user.profile.can_post_messages:
        return JsonResponse({'success': False, 'error': 'You are not allowed to post messages.'})

    # Check if the thread is closed
    if thread.offer and not thread.offer.is_open:
        return JsonResponse({'success': False, 'error': 'This thread is closed and cannot be posted to.'})

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.author = request.user
            message.save()
            is_editable = message.is_editable()
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'author': message.author.username,
                    'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                },
                'is_editable': is_editable,
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid form submission.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@require_POST
@ratelimit(key='ip', rate='3/m')
def message_edit(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    # Check if the user is allowed to post messages
    if not request.user.profile.can_post_messages:
        return JsonResponse({'success': False, 'error': 'You are not allowed to edit messages.'})

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
    
@ratelimit(key='ip', rate='5/m')
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
@ratelimit(key='ip', rate='2/m')
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
@ratelimit(key='ip', rate='5/m')
def thread_delete(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    if request.method == 'POST':
        thread.delete()
        return redirect('thread_list')
    return redirect('thread_detail', thread_id=thread.id)

@login_required
@ratelimit(key='ip', rate='5/m')
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

@ratelimit(key='ip', rate='5/m')
def home(request):
    return render(request, 'home.html', {'is_home': True})

def map(request):
    return render(request, 'map.html')

@ratelimit(key='ip', rate='5/m')
def about(request):
	return render(request, "about.html")

@ratelimit(key='ip', rate='5/m')
def offermain(request):
    show_closed = request.GET.get('show_closed', 'false').lower() == 'true'  # Convert to boolean
    if show_closed:
        offers = Offer.objects.filter(is_open=False)
    else:
        offers = Offer.objects.filter(is_open=True)
    return render(request, "offermain.html", {"offers": offers, "show_closed": show_closed})

def map(request):
    offer_id = request.GET.get('offer_id')
    offer = None
    
    if offer_id:
        try:
            offer = Offer.objects.get(id=offer_id)
        except Offer.DoesNotExist:
            pass
    
    return render(request, 'map.html', {
        'offer': offer,
    })

@ratelimit(key='ip', rate='10/m')
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
@ratelimit(key='ip', rate='5/m')
def create(request):
    if request.method == 'POST':
        form = OfferForm(request.POST, request.FILES)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.user = request.user
            offer.status = 'pending'
            
            # Get coordinates from form data
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            address = request.POST.get('address')
            
            if latitude and longitude:
                offer.latitude = float(latitude)
                offer.longitude = float(longitude)
                offer.address = address
            
            offer.save()
            messages.success(request, 'Your offer has been submitted and is pending approval.')
            return JsonResponse({'success': True})
        else:
            # Return form errors as JSON
            errors = {field: error.get_json_data() for field, error in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    else:
        form = OfferForm()
        
        # Check if there are coordinates in session (fallback method)
        latitude = request.session.pop('selected_latitude', None)
        longitude = request.session.pop('selected_longitude', None)
        address = request.session.pop('selected_address', None)
        
    return render(request, 'create.html', {
        'form': form,
    })

# Add map view
def map(request):
    return render(request, 'map.html')

@ratelimit(key='ip', rate='10/m')
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
@ratelimit(key='ip', rate='5/m')
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
            # Get coordinates from form data
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            address = request.POST.get('address')
            
            # Update coordinates if provided
            if latitude and longitude:
                offer.latitude = float(latitude)
                offer.longitude = float(longitude)
                offer.address = address
            
            # Save the form data
            form.save()
            # Set the status to 'pending' after editing
            offer.status = 'pending'
            offer.save()
            messages.success(request, "Offer updated successfully and is now pending approval.")
            return redirect('item_index', req_id=req_id)
    else:
        form = OfferForm(instance=offer)

    return render(request, 'edit_offer.html', {'form': form, 'offer': offer})

@login_required
@ratelimit(key='ip', rate='10/m')
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
@ratelimit(key='ip', rate='5/m')
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
@ratelimit(key='ip', rate='10/m')
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

        # Create a new thread for the approved offer
    try:
        thread = Thread(
            topic=f"{offer.title}",
            author=offer.user,
            offer=offer
        )
        thread.save()
    except ValidationError as e:
        # Handle the case where the thread cannot be created
        return JsonResponse({'success': False, 'error': str(e)})

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
def toggle_user_post_permission(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_profile = user.profile
    user_profile.can_post_messages = not user_profile.can_post_messages  # Toggle the permission
    user_profile.save()
    messages.success(request, f"{user.username}'s message posting permission has been updated.")
    return redirect('manage_users')

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

@login_required
@ratelimit(key='ip', rate='10/m')
def report_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reported_message = message
            report.reporter = request.user
            report.save()
            return redirect('thread_detail', thread_id=message.thread.id)  # Redirect to the thread detail page
    else:
        form = ReportForm()
    return render(request, 'report_message.html', {'form': form, 'message': message})

@staff_member_required
def view_reports(request):
    reports = Report.objects.filter(status='pending')  # Show only pending reports
    return render(request, 'view_reports.html', {'reports': reports})

@staff_member_required
def resolve_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'restrict':
            # Restrict the reported message
            report.reported_message.is_restricted = True
            report.reported_message.save()
            # Restrict the user from posting further messages
            user_profile = report.reported_message.author.profile
            user_profile.can_post_messages = False
            user_profile.save()
            messages.success(request, f"{report.reported_message.author.username} has been restricted from posting messages.")
        elif action == 'notify':
            # Send a notification to the message author
            send_mail(
                'Message Reported',
                f'Your message in the thread "{report.reported_message.thread.topic}" has been reported. Please review our community guidelines.',
                settings.DEFAULT_FROM_EMAIL,
                [report.reported_message.author.email],
                fail_silently=False,
            )
            messages.success(request, f"A notification has been sent to {report.reported_message.author.username}.")
        report.status = 'resolved'
        report.save()
        return redirect('view_reports')
    return render(request, 'resolve_report.html', {'report': report})


def resend_verification(response):
    if response.method == "POST":
        user_id = response.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            # Delete any existing codes
            VerificationCode.objects.filter(user=user).delete()
            # Generate new code
            verification_code = VerificationCode.generate_code(user)
            # Send email
            send_verification_email(user.email, verification_code.code)
            
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'User not found'
            })
    return JsonResponse({
        'success': False,
        'error': 'Invalid request'
    })

@ratelimit(key='ip', rate='5/m')
def register(response):
    if response.user.is_authenticated:
        return redirect('home')
    
    if response.method == "POST":
        # Check if this is the verification step
        if 'verification_code' in response.POST:
            return handle_verification(response)
        
        # Original registration form handling
        form = RegisterForm(response.POST)
        if form.is_valid():
            # Save user but don't log them in yet
            user = form.save(commit=False)
            user.is_active = False  # User won't be active until verified
            user.save()
            
            # Generate and send verification code
            verification_code = VerificationCode.generate_code(user)
            
            # Send email with verification code
            send_verification_email(user.email, verification_code.code)
            
            # Return success but indicate verification is needed
            return JsonResponse({
                'success': True,
                'verification_required': True,
                'user_id': user.id  # We'll need this for the verification step
            })
        else:
            errors = {field: form.errors[field] for field in form.errors}
            return JsonResponse({'success': False, 'errors': errors})
    else:
        form = RegisterForm()
        
    return render(response, "register.html", {"form": form})

def handle_verification(response):
    user_id = response.POST.get('user_id')
    code = response.POST.get('verification_code')
    
    try:
        user = User.objects.get(id=user_id)
        verification_code = VerificationCode.objects.get(user=user, code=code)
        
        if verification_code.is_valid():
            # Mark code as used
            verification_code.is_used = True
            verification_code.save()
            
            # Activate user
            user.is_active = True
            user.save()
            
            # Log the user in
            login(response, user)
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid or expired verification code'
            })
    except (User.DoesNotExist, VerificationCode.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Invalid verification code'
        })


def send_verification_email(email, code):
    subject = 'Your Verification Code'
    message = f'''
    Hello,
    
    Your verification code is: {code}
    
    This code will expire in 15 minutes.
    
    If you didn't request this, please ignore this email.
    '''
    
    email = EmailMessage(
        subject,
        message,
        to=[email]
    )
    email.send()

@ratelimit(key='ip', rate='2/m')
def request_password_reset(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method.'
        }, status=400)

    email = request.POST.get('email')
    if not email:
        return JsonResponse({
            'success': False,
            'error': 'Email address is required.'
        }, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Don't reveal whether email exists for security
        return JsonResponse({
            'success': True,
            'message': 'If an account exists with this email, you will receive a reset code.'
        })

    # Generate and save verification code
    code = str(secrets.randbelow(999999)).zfill(6)
    request.session['reset_code'] = code
    request.session['reset_user_id'] = user.id
    request.session['reset_code_time'] = str(timezone.now())

    # Send email with HTML template
    subject = 'Password Reset Verification Code'
    context = {
        'code': code,
        'user': user,
        'expiry_minutes': 15
    }
    
    try:
        html_message = render_to_string('password_reset.html', context)
        plain_message = strip_tags(html_message)
        
        email = EmailMessage(
            subject,
            html_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        email.content_subtype = "html"  # Set content to HTML
        email.send()
        
        return JsonResponse({
            'success': True,
            'user_id': user.id,
            'message': 'Verification code sent to your email.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Failed to send verification email. Please try again.'
        }, status=500)

def verify_password_reset(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        
        # Validate the code
        if ('reset_code' not in request.session or 
            'reset_user_id' not in request.session or 
            'reset_code_time' not in request.session):
            return JsonResponse({
                'success': False,
                'error': 'Invalid verification request.'
            })
            
        if (request.session['reset_user_id'] != int(user_id)) or \
           (request.session['reset_code'] != code):
            return JsonResponse({
                'success': False,
                'error': 'Invalid verification code.'
            })
            
        # Check if code is expired (15 minutes)
        code_time = timezone.datetime.fromisoformat(request.session['reset_code_time'])
        if (timezone.now() - code_time) > timedelta(minutes=15):
            return JsonResponse({
                'success': False,
                'error': 'Verification code has expired.'
            })
            
        try:
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            
            # Clear the reset session data
            del request.session['reset_code']
            del request.session['reset_user_id']
            del request.session['reset_code_time']
            
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'User not found.'
            })
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })

@ratelimit(key='ip', rate='3/h')
def resend_reset_code(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method.'
        }, status=400)

    user_id = request.POST.get('user_id')
    if not user_id:
        return JsonResponse({
            'success': False,
            'error': 'User ID is required.'
        }, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found.'
        }, status=404)

    # Generate new code
    code = str(secrets.randbelow(999999)).zfill(6)
    request.session['reset_code'] = code
    request.session['reset_user_id'] = user.id
    request.session['reset_code_time'] = str(timezone.now())

    # Send email with new code
    subject = 'New Password Reset Verification Code'
    context = {
        'code': code,
        'user': user,
        'expiry_minutes': 15
    }
    
    try:
        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = strip_tags(html_message)
        
        email = EmailMessage(
            subject,
            html_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        email.content_subtype = "html"
        email.send()
        
        return JsonResponse({
            'success': True,
            'message': 'New verification code sent to your email.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Failed to send new verification code. Please try again.'
        }, status=500)
    
from django.http import JsonResponse

def rate_limit_view(request, exception):
    return JsonResponse({
        'error': 'Too many requests. Please try again later.'
    }, status=429)