from django.urls import path
from accounts import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='account_signup'),
    path('signup/confirm/', views.SignupConfirmView.as_view(), name='account_signup_confirm'),
    path('signup/temporary/', views.SignupDoneView.as_view(), name='account_signup_done'),
    path('signup/thanks/<token>/', views.SignupCompleteView.as_view(), name='account_signup_complete'),
    path('staffsignup/', views.StaffSignupView.as_view(), name='account_staff_signup'),
    path('login/', views.LoginView.as_view(), name='account_login'),
    path('logout/', views.LogoutView.as_view(), name='account_logout'),
]
