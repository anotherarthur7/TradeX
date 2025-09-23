from django.urls import path
from . import views
from .views import resend_verification
from .views import request_password_reset, verify_password_reset, resend_reset_code

urlpatterns = [
    path("", views.home, name="home"),
    path('register', views.register, name='register'),
    path('logout', views.logout_view, name='logout'),
    path('login', views.login_view, name='login'),
    path("home", views.home, name="home"),
    path("about", views.about, name="about"),
    path("create", views.create, name="create"),
    path("offermain", views.offermain, name="offermain"),
    path('forum/', views.thread_list, name='thread_list'),
    path('forum/thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('resend-verification/', resend_verification, name='resend_verification'),
    path('forum/thread/create/', views.thread_create, name='thread_create'),
    path('forum/thread/<int:thread_id>/delete/', views.thread_delete, name='thread_delete'),
    path('forum/message/<int:message_id>/delete/', views.message_delete, name='message_delete'),
    path('message/<int:message_id>/edit/', views.message_edit, name='message_edit'),
    path("offermain/<int:req_id>", views.itemIndex, name="itemIndex"),
    path('offer/<int:req_id>/', views.itemIndex, name='item_index'),  
    path('offer/<int:req_id>/edit/', views.edit_offer, name='edit_offer'),
    path('offer/<int:req_id>/delete/', views.delete_offer, name='delete_offer'),
    path('profile/', views.profile, name='profile'),
    path('my-offers/', views.my_offers, name='my_offers'),
    path('review-offers/', views.review_offers, name='review_offers'),
    path('approve-offer/<int:offer_id>/', views.approve_offer, name='approve_offer'),
    path('reject-offer/<int:offer_id>/', views.reject_offer, name='reject_offer'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('forum/report/<int:message_id>/', views.report_message, name='report_message'),
    path('admin/reports/', views.view_reports, name='view_reports'),
    path('admin/reports/resolve/<int:report_id>/', views.resolve_report, name='resolve_report'),
    path('thread/<int:thread_id>/message/create/', views.message_create, name='message_create'),
    path('admin/toggle-post-permission/<int:user_id>/', views.toggle_user_post_permission, name='toggle_user_post_permission'),
    path('request-password-reset/', request_password_reset, name='request_password_reset'),
    path('verify-password-reset/', verify_password_reset, name='verify_password_reset'),
    path('resend-reset-code/', resend_reset_code, name='resend_reset_code'),
    path('map/', views.map, name='map'),  # Add this line
]