import os

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegisterForm(forms.Form):
    full_name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label='Confirm Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        email: str = cleaned_data.get('email')
        password: str = cleaned_data.get("password")
        password_2: str = cleaned_data.get("confirm_password")

        qs = User.objects.filter(email=email).exists()
        if qs:
            raise forms.ValidationError(
                _(f"a user with {email} already exists"), code=409)

        if len(password) < 8:
            raise forms.ValidationError(
                _(f"Password must be at least 8 characters"))

        if password is not None and password != password_2:
            raise forms.ValidationError(_(f"Both passwords must match"))

        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        super(LoginForm, self).clean()

        email: str = self.cleaned_data.get('email')
        password: str = self.cleaned_data.get('password')

        if '@' not in email:
            raise forms.ValidationError(f"Invalid email type provided")

        if len(password) < 8:
            raise forms.ValidationError(
                f"Password must be at least 8 characters")

        return self.cleaned_data


class PasswordChangingForm(PasswordChangeForm):
    # add attributes to password
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password1 = forms.CharField(
        max_length=100, widget=forms.PasswordInput())
    new_password2 = forms.CharField(
        max_length=100, widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


class UpdateUserForm(forms.ModelForm):
    email = forms.CharField(disabled=True, widget=forms.TextInput
                            (attrs={'placeholder': f'email', 'class':
                                    'border rounded-[10px] w-[483px] h-[43px] pl-[20px] mt-[5px] bg-[#FBFBFB] outline-none '}))
    full_name = forms.CharField(widget=forms.TextInput
                                (attrs={'placeholder': f'full_name', 'class':
                                        'border rounded-[10px] w-[483px] h-[43px] pl-[20px] mt-[5px] bg-[#FBFBFB] outline-none '}))

    mobile = forms.CharField(widget=forms.TextInput
                             (attrs={'placeholder': f'mobile', 'class':
                                     'border rounded-[10px] w-[483px] h-[43px] pl-[20px] mt-[5px] bg-[#FBFBFB] outline-none '}))

    username = forms.CharField(widget=forms.TextInput
                               (attrs={'placeholder': f'username', 'class':
                                       'border rounded-[10px] w-[483px] h-[43px] pl-[20px] mt-[5px] bg-[#FBFBFB] outline-none '}))

    photo = forms.ImageField(
        required=False, widget=forms.FileInput(), error_messages={'invalid': ""})

    class Meta:
        model = User
        fields = ('email', 'full_name', 'username', 'mobile', 'photo')
