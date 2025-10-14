from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('api/check-user/', views.check_user, name='check_user'),
    path('api/send-otp/', views.send_otp, name='send_otp'),
    path('api/verify-otp/', views.verify_otp, name='verify_otp'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('api/profile/', views.user_profile, name='user_profile'),
]
