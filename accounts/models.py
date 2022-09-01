from typing import List
from PIL import Image

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MaxLengthValidator

from .manager import UserManager


class User(AbstractUser):
    """
    User model inherited from AbstractUser to add new fields to the models
    """
    username = models.CharField(
        max_length=50, unique=True, null=True, blank=True)
    email = models.EmailField(_('email address'), max_length=150, unique=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    mobile = models.CharField(max_length=50)
    photo = models.ImageField(
        upload_to="profile_images", null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    last_logout_time = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD: str = 'email'
    REQUIRED_FIELDS: List[str] = ['full_name']

    def save(self, *args, **kwargs):
        super(User, self).save()
        if self.photo:
            img = Image.open(self.photo.path)
            if img.height > 200 or img.width > 200:
                new_img = (200, 200)
                img.thumbnail(new_img)
                img.save(self.photo.path)

    def get_full_name(self):
        return f'{self.full_name}'

    def __str__(self):
        return self.full_name

    # def get_absolute_url(self):
    #     return reverse("profile", args=[str(self.user)])
