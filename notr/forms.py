from django import forms
from django.contrib.auth import get_user_model
from .models import Comment, Notes
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.widgets import CKEditor5Widget

User = get_user_model()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class ShareForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label='Confirm Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(ShareForm, self).clean()
        password: str = cleaned_data.get('password')
        confirm_password: str = cleaned_data.get("confirm_password")

        if len(password) < 8:
            raise forms.ValidationError(
                _(f"Password must be at least 8 characters"))

        if password is not None and password != confirm_password:
            raise forms.ValidationError(_(f"Both passwords must match"))

        return cleaned_data


class NotesForm(forms.ModelForm):
    """Form for Notes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["body"].required = False

    def clean(self):
        print(super().clean)

    class Meta:
        model = Notes
        fields = ("body",)
        widgets = {
            "body": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            )
        }


class EditForm(forms.ModelForm):
    """Form for Notes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["body"].required = False

    def clean(self):
        print(super().clean)

    class Meta:
        model = Notes
        fields = ("body",)
        widgets = {
            "body": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5", "value": f"body"}, config_name="extends"
            )
        }
