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
    path('forum/', views.thread_list, name='thread_list'),
    path('forum/thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('forum/thread/create/', views.thread_create, name='thread_create'),
    path('forum/thread/<int:thread_id>/delete/', views.thread_delete, name='thread_delete'),
    path('forum/message/<int:message_id>/edit/', views.message_edit, name='message_edit'),
    path("offermain/<int:req_id>", views.itemIndex, name="itemIndex"),
    path('offer/<int:req_id>/', views.itemIndex, name='item_index'),  # Ensure this line exists
    path('offer/<int:req_id>/edit/', views.edit_offer, name='edit_offer'),
    path('offer/<int:req_id>/delete/', views.delete_offer, name='delete_offer'),
    path('profile/', views.profile, name='profile'),
    path('my-offers/', views.my_offers, name='my_offers'),
]