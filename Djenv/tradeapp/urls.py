from django.urls import path
from . import views

urlpatterns = [
	path("", views.home, name="home"),
    path("about", views.about, name="about"),
    path("offermain", views.offermain, name="offermain"),
    path("offermain/<int:req_id>", views.itemIndex, name="itemIndex")
]