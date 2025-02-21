from django.urls import path
from . import views

urlpatterns = [
	path("", views.home, name="home"),
    #path("offers", views.items, name="offers"),
    path("<int:req_id>", views.itemIndex, name="itemIndex")
]