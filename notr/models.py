import time
import datetime

from genericpath import exists
from django.db import models
from django.core.validators import MinLengthValidator
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.db.models import Q
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
from helpers.notes_password import hash_password
from django_ckeditor_5.fields import CKEditor5Field

from django.conf import settings

User = settings.AUTH_USER_MODEL


class DefaultSet(models.Manager):
    def get_queryset(self):
        return super().get_queryset().all()


class NormalSet(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(Q(is_archived=False) & Q(is_trashed=False))


class ArchivedSet(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=True)


class TrashedSet(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_trashed=True)


def _json(name):
    return list


class Notes(models.Model):

    VIEWONLY = 'VO'
    VIEWEDIT = 'VE'

    CHOICES = [
        (VIEWONLY, 'View only'),
        (VIEWEDIT, 'View and edit'),
    ]

    title = models.CharField(max_length=150)
    images = models.ImageField(upload_to="notes_images", null=True, blank=True)
    files = models.FileField(upload_to="notes_files", null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    is_trashed = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User, related_name="users", on_delete=models.PROTECT, null=True)
    public = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True)
    labels = models.JSONField(default=_json('labels'))
    has_password = models.BooleanField(default=False)
    password = models.CharField(max_length=255, blank=True, null=True)
    body = CKEditor5Field('body', config_name="extends")
    invites = models.JSONField(default=_json('invites')),
    is_shared = models.BooleanField(default=False)
    view_type = models.CharField(
        max_length=2, choices=CHOICES, default=VIEWONLY)

    class Meta:
        permissions = [
            ("can_edit_notes", "can edit notes"),
            ("can_view_notes", "can view notes"),
        ]
        verbose_name = 'notes'
        verbose_name_plural = 'notes'

    objects = DefaultSet()
    _normal_objects = NormalSet()
    _archived_objects = ArchivedSet()
    _trash_objects = TrashedSet()

    def __str__(self):
        return f"{self.title}"

    def save(self):
        if self.password:
            self.password = hash_password(self.password)
        return super().save()

    def _archive(self):
        self.is_archived = True
        return super().save()

    def _unarchive(self):
        self.is_archived = False
        return super().save()

    def _pin(self):
        self.is_pinned = True
        return super().save()

    def _unpin(self):
        self.is_pinned = False
        return super().save()

    def _trash(self):
        self.is_trashed = True
        return super().save()

    def _untrash(self):
        self.is_trashed = False
        return super().save()

    def get_absolute_url(self):
        # return reverse('cape:post', args=str(self.slug))
        pass


@receiver(post_save, sender=Notes)
def set_permission(sender, instance, **kwargs):
    assign_perm("can_edit_notes", instance.owner, instance)
    assign_perm("can_view_notes", instance.owner, instance)


class Labels(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE, related_name="labels")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'label'
        verbose_name_plural = 'labels'


class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='comments')
    text = models.CharField(max_length=400)
    note = models.ForeignKey(
        Notes, on_delete=models.CASCADE, related_name="comments")
    timestamp = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.user}: {self.text}"
