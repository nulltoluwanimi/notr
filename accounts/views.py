from contextlib import redirect_stderr
from glob import escape
import uuid
import os
import json
from typing import Dict, Any
from urllib import request
from dotenv import load_dotenv

from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView, UpdateView, View
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm

from .forms import RegisterForm, LoginForm, PasswordChangingForm, UpdateUserForm
from helpers.email_config import send_mail_func

User = get_user_model()
load_dotenv()


class UserMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/login/'

    def test_func(self):
        if self.request.user.id == self.kwargs['pk']:
            return True
        return False


def home_page(request):
    return render(request, "accounts/home.html")


class Register(View):
    def get(self, request):
        return render(request, "accounts/register.html")

    def post(self, request):
        logout(self.request)
        register_details = RegisterForm(self.request.POST)
        # validating form fields
        if register_details.is_valid():
            try:
                # get cleaned data from register form
                email = register_details.cleaned_data['email']
                password = register_details.cleaned_data['password']
                full_name = register_details.cleaned_data['full_name']
                new_user = User.objects.create_user(
                    email=email, password=password, full_name=full_name, )
                print(new_user.pk)
                current_site = get_current_site(self.request)
                uid = urlsafe_base64_encode(force_bytes(new_user.pk))
                token = default_token_generator.make_token(new_user)

                email_body = {
                    'token': token,
                    'subject': "Recover Password Mail.",
                    'messages': f'Hi, mate. continue with http://{current_site}/verify-mail/{uid}/{token} to verify your email, Thanks',
                    'recipients': [email]
                }
                send_mail_func(email_body)
                messages.success(
                    self.request, f'a verification email has been sent to {email}')
                return redirect('accounts:login')

            except Exception as e:
                print(e)
                messages.error(
                    self.request, 'Internal server error, please try again later')
                return render(request, "accounts/register.html")

        else:

            error = (register_details.errors.as_text()).split('*')
            messages.error(self.request, error[len(error)-1])
            return render(request, "accounts/register.html", )


class LoginUser(View):
    def get(self, request):
        return render(request, "accounts/login.html")

    def post(self, request):
        logout(self.request)
        login_details = LoginForm(self.request.POST)
        email = self.request.POST['email']
        password = self.request.POST['password']

        if not email or not password:
            messages.info(
                self.request, 'Both Username and Password must be provided')
        # validating form fields
        if login_details.is_valid():
            try:
                user = authenticate(email=email, password=password)
                if user:
                    # messages.success(self.request, 'Login Successful')
                    login(request, user)
                    return HttpResponseRedirect(reverse('notr:note-home', args=('normal',)))
                else:
                    messages.error(self.request, 'Wrong username or password')
                    return HttpResponseRedirect(reverse('accounts:login'))
            except Exception as e:
                print(e)
                messages.error(
                    self.request, 'Internal server error, please try again later')
                return HttpResponseRedirect(reverse('accounts:login'))

        else:

            error = (login_details.errors.as_text()).split('*')
            messages.error(self.request, error[len(error)-1])
            return render(request, "accounts/login.html",)


class Logout(View):
    @method_decorator(login_required)
    def get(self, request):
        user: Dict[Any] = User.objects.get(pk=request.user.id)
        user.last_logout_time = timezone.now()
        user.save()
        logout(self.request)
        return render(request, "accounts/home.html")


class PasswordChange(UserMixin, PasswordChangeView):
    def get(self, request, pk):
        return render(request, 'accounts/edit_profile.html')

    def post(self, request, pk):
        try:
            form = PasswordChangeForm(request.user)
            if request.method == 'POST':
                form = PasswordChangeForm(request.user, request.POST)
                if form.is_valid():
                    user = form.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'password changed successfully')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                error = (form.errors.as_text()).split('*')
                messages.error(self.request, error[len(error)-1])
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            return HttpResponseRedirect(reverse('accounts:edit-password', args=(request.user.id,)))

        except:
            pass


class RecoverPassword(View):
    def get(self, request, *args, **kwargs):
        return render(request, "accounts/reset_password.html")

    def post(self, request):
        try:
            email = self.request.POST.get('email')
            user = User.objects.get(email=email)
            current_site = get_current_site(self.request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            email_body = {
                'token': token,
                'subject': "Recover Password Mail.",
                'messages': f'Hi, {user.username}. continue http://{current_site}/password-token/{uid}/{token} to change your password, Thanks',
                'recipients': email
            }
            send_mail_func(email_body)
            messages.success(request, f'An email has been sent to {email}')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except User.DoesNotExist:
            messages.info(
                self.request, 'Hmmm!, cant find user with the email provided')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ResetPassword(View):
    def get(self, request, uid, token):
        return render(request, 'accounts/new_password.html', {'uid': uid, 'token': token})

    def post(self, request, uid, token):
        try:
            uid_decode = urlsafe_base64_decode(uid)
            user = User.objects.get(pk=uid_decode)
            if default_token_generator.check_token(user, token):
                password = request.POST["password"]
                confirm_password = request.POST["confirm_password"]

                if password == confirm_password:
                    user.set_password(password)
                    user.save()
                    messages.success(
                        self.request, "Password changed successfully, you can now login")
                    return redirect('accounts:login')
                else:
                    messages.error(self.request, "Password does not match")
                    return render(request, 'accounts/new_password.html', {'uid': uid, 'token': token})
            else:
                messages.error(
                    self.request, "Token does not seems to be valid")
                return render(request, 'accounts/new_password.html', {'uid': uid, 'token': token})
        except Exception as e:
            messages.error(request, "Seems the link has expired!, try again")
            return redirect('accounts:login')


class EditUser(UserMixin, UpdateView):
    model = User
    form_class = UpdateUserForm
    template_name = 'accounts/edit_profile.html'

    def get_success_url(self):
        return reverse_lazy('accounts:edit-user', kwargs={'pk': self.request.user.id})


class VerifyUser(View):
    def get(self, request, uid, token):
        try:
            uid_decode = urlsafe_base64_decode(uid)
            user = User.objects.get(pk=uid_decode)
            if default_token_generator.check_token(user, token):
                if default_token_generator.check_token(user, token) and user.is_verified:
                    print('check_token')
                    return redirect('accounts:verify-status', uid=str(uid), success=None)

                user.is_verified = True
                user.save()
                return redirect('accounts:verify-status', uid=str(uid), success=True)

        except Exception as e:
            return redirect('accounts:verify-status',  uid=str(uid), success=False)


def verification_message(request, uid, success):
    try:
        print(success)
        uid_decode = urlsafe_base64_decode(uid)
        user = User.objects.get(pk=uid_decode)
        if 'None' not in success:
            messages.success(
                request, f"{user.email} is successfully verified.")
            return render(request, "accounts/verify_mail.html")
        else:
            messages.info(request, f"{user.email} already verified")
            return render(request, "accounts/verify_mail.html")
    except User.DoesNotExist:
        messages.error(request, "Seems the link has expired!, try again")
        return render(request, "accounts/verify_mail.html")

        # return redirect('accounts:verify-status',  uid=str(uid), success=False)
