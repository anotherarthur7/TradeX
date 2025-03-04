from django.urls import path
from . import views
import register.views as v


urlpatterns = [
	path("", views.home, name="home"),
    path('register', v.register, name='register'),
    path('logout', views.logout_view, name='logout'),
    path('login', views.login_view, name='login'),
    path("home", views.home, name="home"),
    path("about", views.about, name="about"),
    path("create", views.create, name="create"),
    path("offermain", views.offermain, name="offermain"),
    path("offermain/<int:req_id>", views.itemIndex, name="itemIndex"),
    path('offer/<int:req_id>/', views.itemIndex, name='item_index'),  # Ensure this line exists
    path('offer/<int:req_id>/edit/', views.edit_offer, name='edit_offer'),
    path('offer/<int:req_id>/delete/', views.delete_offer, name='delete_offer'),
]