from django.db import models


# Create your models here.


class Offer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='images/', blank=True, null=True) # Optional image
    posted_date = models.DateTimeField(auto_now_add=True) # Automatically set on creation
    #seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')  #One-to-many: User can have multiple offers

    def __str__(self):
        return self.title
