#create_profiles.py
from django.contrib.auth.models import User
from tradeapp.models import Profile

# Loop through all users
for user in User.objects.all():
    print(f"Checking user: {user.username}")
    if not hasattr(user, 'profile'):
        print(f"Creating profile for user: {user.username}")
        Profile.objects.create(user=user)
    else:
        print(f"Profile already exists for user: {user.username}")