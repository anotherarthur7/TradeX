from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from datetime import timedelta
import secrets
from django.core.exceptions import ValidationError
# Create your models here.


class Offer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    posted_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    is_open = models.BooleanField(default=True) 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending') 
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='images/', blank=True, null=True)
    can_post_messages = models.BooleanField(default=True)  # Allow users to post messages by default

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Thread(models.Model):
    topic = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='threads', null=True, blank=True)
    is_technical = models.BooleanField(default=False)

    def __str__(self):
        return self.topic

    def save(self, *args, **kwargs):
        # Ensure that a thread cannot be manually created for a non-approved offer
        if self.offer and self.offer.status != 'approved':
            raise ValidationError("A thread can only be created for an approved offer.")
        super().save(*args, **kwargs)

class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_restricted = models.BooleanField(default=False)  # To restrict access to the message

    def is_editable(self):
        # Check if the message is editable (within 10 minutes of creation)
        time_elapsed = timezone.now() - self.created_at
        return time_elapsed.total_seconds() <= 600  # 10 minutes = 600 seconds

    def __str__(self):
        return f'Message by {self.author.username} in {self.thread.topic}'
    
class Report(models.Model):
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('hate_speech', 'Hate Speech'),
        ('inappropriate_content', 'Inappropriate Content'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
    ]

    reported_message = models.ForeignKey('Message', on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_submitted')
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    message = models.TextField(blank=True, null=True)  # Optional additional message
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report #{self.id} - {self.reported_message}"
    
class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def is_valid(self):
        return not self.is_used and (timezone.now() - self.created_at) < timedelta(minutes=15)
    
    @classmethod
    def generate_code(cls, user):
        # Delete any existing codes for this user
        cls.objects.filter(user=user).delete()
        
        # Generate a new 6-digit code
        code = str(secrets.randbelow(999999)).zfill(6)
        return cls.objects.create(user=user, code=code)