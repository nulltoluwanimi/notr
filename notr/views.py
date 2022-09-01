
from typing import Dict, Any
from dotenv import load_dotenv
import time
import datetime


from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView, UpdateView, View
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseNotFound, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.db.models import Q
from django.template.defaultfilters import slugify


from helpers.notes_password import hash_password, check_password

from helpers.email_config import send_mail_func
from .models import Notes, Labels, Comment
from .forms import CommentForm, ShareForm, NotesForm, EditForm

User = get_user_model()
load_dotenv()


def handle_404(request, exception=None):
    return HttpResponseNotFound(render(request, '404.html'))


def handle_403(request, exception=None):
    return HttpResponseForbidden(render(request, '401.html'))


class NotesMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        if self.request.user.id == self.kwargs['pk']:
            return True
        return False


class GetAllNotes(LoginRequiredMixin, ListView):
    model = Notes
    template_name = 'notr/notes_home.html'

    def get_queryset(self):
        query = self.request.GET.get('query', '')
        qs = Notes._normal_objects.filter(
            Q(owner_id=self.request.user.id) & Q(title__icontains=query))
        return qs.order_by('-is_pinned')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['type'] = self.kwargs.get('type', '')
        label = self.kwargs.get('label', '')
        context['label'] = label
        context['label_items'] = Notes._normal_objects.filter(
            Q(owner_id=self.request.user.id) & Q(labels__icontains=label))
        context['label_info'] = Labels.objects.filter(
            name__iexact=label)

        return context


class CreateNotes(NotesMixin, View):

    def get(self, request, *args, **kwargs):
        form = NotesForm()
        return render(request, "notr/create_notes.html", {'form': form})

    def post(self, request, *args, **kwargs):
        form = NotesForm(request.POST, request.FILES)

        if form.is_valid():
            body = form.cleaned_data.get('body')
            label = request.POST.get('labels')
            title = request.POST.get('title')

            check_note = Notes.objects.filter(
                Q(title__iexact=title) & Q(owner_id=self.request.user.id))
            if check_note.exists():
                messages.info(self.request, "Note title already exists")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            note = Notes.objects.filter(title=title)

            if not note.exists():
                slug = slugify(title)
            else:

                slug = slugify(title) + \
                    str(time.mktime(datetime.datetime.now().timetuple())[:5])
                title = title + '-' + str(check_note.count() + 1)
            # print(list(label))

            note = Notes(title=title, body=body,
                         labels=[label], owner=request.user, slug=slug)
            note.save()
            success_url = reverse(
                "notr:view-note", kwargs={"pk": self.request.user.id, "note_id": note.id})
            return HttpResponseRedirect(success_url)
        else:
            error = (form.errors.as_text()).split('*')
            messages.error(self.request, error[len(error)-1])
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class EditNote(NotesMixin, View):
    def get(self, request, pk, note_id):
        try:
            form = EditForm()
            note = Notes.objects.get(pk=note_id)
            return render(request, "notr/edit_notes.html", {"pk": self.request.user.id,
                                                            "note_id": note_id, "note": note, "form": form})
        except Notes.DoesNotExist:
            error_url = reverse(
                "notr:view-note", kwargs={"pk": self.request.user.id, "note_id": note_id})
            return HttpResponseRedirect(error_url)

    def post(self, request, *args, **kwargs):
        form = NotesForm(request.POST, request.FILES)

        if form.is_valid():
            body = form.cleaned_data.get('body')
            label = request.POST.get('labels')
            title = request.POST.get('title')
            print(label)

            check_note = Notes.objects.get(pk=self.kwargs.get('note_id'))
            print(check_note)

            if check_note:
                check_note.body = body
                check_note.labels = [label]
                check_note.title = title
                # check_note.slug = slugify(title)
                check_note.save()

            success_url = reverse(
                "notr:view-note", kwargs={"pk": self.request.user.id, "note_id": check_note.pk})
            return HttpResponseRedirect(success_url)
        else:
            error = (form.errors.as_text()).split('*')
            messages.error(self.request, error[len(error)-1])
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class EditNotePublic(View):
    def get(self, request, note_id):
        try:
            form = EditForm()
            uid_decode = urlsafe_base64_encode(force_bytes(note_id))
            note = Notes.objects.get(pk=uid_decode)
            return render(request, "notr/edit_notes.html", {"pk": self.request.user.id,
                                                            "note_id": note.id, "note": note, "form": form})
        except Notes.DoesNotExist:
            error_url = reverse(
                "notr:view-note", kwargs={"pk": self.request.user.id, "note_id": note_id})
            return HttpResponseRedirect(error_url)

    def post(self, request, note_id):

        form = NotesForm(request.POST, request.FILES)

        if form.is_valid():
            body = form.cleaned_data.get('body')
            label = request.POST.get('labels')
            title = request.POST.get('title')
            # print(label)

            check_note = Notes.objects.get(pk=self.kwargs.get('note_id'))
            print(check_note)

            if check_note:
                check_note.body = body
                check_note.labels = [label]
                check_note.title = title
                # check_note.slug = slugify(title)
                check_note.save()

            return render(request, 'notr/ notes_view.html', {'note': check_note})

        else:
            error = (form.errors.as_text()).split('*')
            messages.error(self.request, error[len(error)-1])
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class DeleteNote(NotesMixin, View):
    def get(self, request, pk, note_id):
        try:
            Notes.objects.get(id=note_id).delete()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Notes.DoesNotExist:
            messages.error(
                request, f"Error Performing this action")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class TrashNote(NotesMixin, View):
    def get(self, request, pk, note_id):
        try:
            notes = Notes.objects.get(id=note_id)
            print(notes)
            if not notes.is_trashed:
                notes._trash()
                notes._unarchive()
                notes._unpin()

            else:
                notes._untrash()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Notes.DoesNotExist:
            messages.error(
                request, f"Error Performing this action")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PinNote(NotesMixin, View):
    def get(self, request, pk, note_id):
        try:
            notes = Notes.objects.get(id=note_id)
            if not notes.is_pinned:
                notes._pin()
            else:
                notes._unpin()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Notes.DoesNotExist:
            messages.error(
                request, f"Error Performing this action")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ArchiveNote(NotesMixin, View):
    def get(self, request, pk, note_id):
        try:
            notes = Notes.objects.get(pk=note_id)
            print('here', notes, notes.is_archived)
            if not notes.is_archived:
                notes._archive()
                notes._untrash()
                notes._unpin()
            else:
                notes._unarchive()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Notes.DoesNotExist:
            messages.error(
                request, f"Error Performing this action")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ViewNoteUser(NotesMixin, View):
    def get(self, request, pk, note_id):
        try:
            notes = Notes.objects.get(pk=note_id)
            print(type(notes.labels))
            uid_decode = urlsafe_base64_encode(force_bytes(note_id))
            link = f'{get_current_site(request)}/notes/{uid_decode}/{notes.slug}'
            context = {
                "notes": notes,
                "link": link,
            }
            return render(request, 'notr/notes_details.html', context)

        except Notes.DoesNotExist:
            messages.error(
                request, f"Error Performing this action")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ShareNotes(NotesMixin, View):
    def post(self, request, pk, note_id):
        try:
            notes = Notes.objects.get(pk=note_id)
            print(request.POST)
            password = request.POST.get('password')
            view = request.POST.get('permission')

            if password:
                validate_form = ShareForm(request.POST)
                print(validate_form.is_valid())
                if validate_form.is_valid():
                    notes.password = password
                    notes.has_password = True
                    notes.is_shared = True
                    notes.view_type = view
                    notes.save()
                    messages.success(self.request, "shared status created")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    error = (validate_form .errors.as_text()).split('*')
                    messages.error(request, error[len(error)-1])
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            notes.is_shared = True
            notes.view_type = view
            notes.save()
            messages.success(self.request, "shared status created")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Notes.DoesNotExist:
            messages.error(
                request, f"Error Performing this action")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def add_invites(request, notes_id, email,):
    try:
        public = request.POST.get('public')
        password = request.POST.get('password')

        if not public:
            password = hash_password(password)
            find_user = User.objects.get(email__iexact=email)
            notes = notes._normal_objects.filter(pk=notes_id)
            notes.invites.append(email)
            notes.public = False
            notes.password = hash_password
            notes.save()

            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(notes.pk))
            email_body = {
                'subject': f"Invites to {notes.title}.",
                'messages': f'Hi, mate. {find_user.full_name} has invited you to {notes.title}, continue with http://{current_site}/notes/{uid} , Thanks',
                'recipents': [email]
            }
            send_mail_func(email_body)
            messages.success(request, f'Invites sent to {email} ')
            # return render
            pass
        find_user = User.objects.get(email__iexact=email)
        notes = notes._normal_objects.filter(pk=notes_id)
        notes.invites.append(email)
        notes.save()
        pass

        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(notes.pk))
        email_body = {
            'subject': f"Invites to {notes.title}.",
            'messages': f'Hi, mate. {find_user.full_name} has invited you to {notes.title}, continue with http://{current_site}/notes/{uid} , Thanks',
            'recipents': [email]
        }
        send_mail_func(email_body)
        messages.success(request, f'Invites sent to {email} ')

    except User.DoesNotExist:
        messages.info(request, '')


def check_notes_password(request, slug):

    try:
        if request.method == 'POST':
            uid = request.POST.get('uid')
            # print(111, uid)
            # uid_decode = urlsafe_base64_decode(uid)
            # print(11, uid, uid_decode)
            notes = Notes._normal_objects.get(slug=slug)
            password = request.POST.get('password', '')
            print(check_password(notes.password, password), password)
            if check_password(notes.password, password):
                messages.success(request, 'Correct✔️')
                success_url = reverse(
                    "notr:notes", args={"uid": uid, "slug": notes.slug})
                return HttpResponseRedirect(success_url)

            messages.error(request, 'InCorrect')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except Exception as e:
        print(e)
        messages.error(
            request, 'Something went wrong, please contact the owner')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ViewNotes(View):
    def get(self, request, uid, slug):
        try:
            check = request.GET.get('check', None)
            uid_decode = urlsafe_base64_decode(uid)
            notes = Notes._normal_objects.get(pk=uid_decode)
            print(notes.is_shared)
            if notes.is_shared and not notes.has_password and not check:
                # render notes if public and no check
                return render(request, 'notr/notes_view.html', {'note': notes})
            if notes.is_shared and notes.has_password and not check:
                # check if not public and check, return password template
                # notes_owners = notes.full_name
                return render(request, 'notr/check_note_password.html', {'uid': uid, 'note': notes})
            if notes.is_shared and notes.has_password and check:

                return render(request, 'notr/ notes_view.html', {'note': notes})
                # check if not public and  not check
            if not notes.is_shared:
                messages.error(
                    request, 'Something went wrong, fetching notes, ask the owner for a recheck, it might be caused, if the owner forgot to share')
                return render(request, 'notr/notes_view.html',)

        except Notes.DoesNotExist:
            messages.error(
                request, 'Something went wrong, fetching notes, ')
            return render(request, 'notr/notes_view.html',)
    # def post(self, request):
    #     try:

    #     except:


@login_required(login_url='login/')
def pin_notes(self, request, user_id, notes_id):
    try:
        find_user = User.objects.get(id=user_id)
        if Notes._normal_objects.filter(Q(owner_id=user_id) & Q(is_pin=True)).count() == 3:
            messages.info(
                request, f"Hey,{find_user.full_name}!, you can only pin 3 notes")
            # return render(request)
            pass
        note = Notes.objects.get(pk=notes_id)
        note.is_pinned = True
        note.save()
        # return render(request)
        pass

    except Exception as e:
        pass


@login_required()
def add_labels(request):
    try:
        if request.method == 'POST':
            label = request.POST.get('labels')
            description = request.POST.get('description')
            print(label, description)
            new_label = Labels(
                name=label, description=description, user=request.user)
            print(new_label)
            new_label.save()
            messages.info(
                request, f"Labels added successfully")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except Exception as e:
        messages.error(
            request, f"Error adding label")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class AddComment(View):
    def post(self, request, pk):
        try:
            validate = CommentForm(request.POST)
            if validate.is_valid():
                note = Notes.objects.get(pk=pk)
                new_comment = Comment(
                    text=request.POST.get('text'),
                    user_id=self.request.user.id,
                    notes_id=note.id
                )
                new_comment.save()
            response = {
                "status": 200,
                "success": True,
                "message": "Comment add to post",
                "data": request.POST,

            }
            return JsonResponse(response)

        except Exception as e:
            response = {
                "status": 500,
                "success": False,
                "message": "Error adding comment to post",
                "reason": e
            }
