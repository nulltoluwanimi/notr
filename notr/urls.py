
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'notr'
urlpatterns = [
    path('notes-home/<str:type>', views.GetAllNotes.as_view(), name='note-home'),
    path('label/<str:label>', views.GetAllNotes.as_view(), name='note-label'),
    path('add-label/', views.add_labels, name='add-label'),
    path('archive-note/<int:pk>/<int:note_id>',
         views.ArchiveNote.as_view(), name='archive-note'),
    path('trash-note/<int:pk>/<int:note_id>',
         views.TrashNote.as_view(), name='trash-note'),
    path('delete-note/<int:pk>/<int:note_id>',
         views.DeleteNote.as_view(), name='delete-note'),
    path('pin-note/<int:pk>/<int:note_id>',
         views.PinNote.as_view(), name='pin-note'),
    path('view-note/<int:pk>/<int:note_id>',
         views.ViewNoteUser.as_view(), name='view-note'),
    path('share-note/<int:pk>/<int:note_id>/',
         views.ShareNotes.as_view(), name='share-note'),
    path('notes/<str:uid>/<slug:slug>',
         views.ViewNotes.as_view(), name='notes'),
    path('check/password/<str:uid>',
         views.check_notes_password, name="check-password"),
    path('add-notes/<int:pk>', views.CreateNotes.as_view(), name='add-note'),
    path('edit-notes/<int:pk>/<int:note_id>/',
         views.EditNote.as_view(), name='edit-note'),
    path('notes/<str:note_id>/',
         views.EditNotePublic.as_view(), name='edit-public-note')
]
