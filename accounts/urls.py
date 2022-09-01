
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'accounts'
urlpatterns = [
    path('', views.home_page, name='home'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('registration/', views.Register.as_view(), name='register'),
    path('verify-mail/<str:uid>/<str:token>/',
         views.VerifyUser.as_view(), name='verify-mail'),
    path('verification-status/<str:uid>/<str:success>/',
         views.verification_message, name='verify-status'),
    path('reset-password/', views.RecoverPassword.as_view(), name='reset-password'),
    path('password-token/<str:uid>/<str:token>/',
         views.ResetPassword.as_view(), name='set-password'),
    path('edit/profile/<int:pk>', views.EditUser.as_view(), name='edit-user'),
    path('edit/change-password/<int:pk>',
         views.PasswordChange.as_view(), name='edit-password'),
    path('logout/', views.Logout.as_view(), name='logout'),

]
