# tradeapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Offer, Thread

@receiver(post_save, sender=Offer)
def create_thread_for_offer(sender, instance, created, **kwargs):
    """
    Automatically create a thread when a new offer is posted.
    """
    if created:  # Only create a thread for new offers
        Thread.objects.create(
            topic=instance.title,  # Use the offer's title as the thread topic
            author=instance.user,  # Set the thread author to the offer's creator
            offer=instance,  # Link the thread to the offer
        )