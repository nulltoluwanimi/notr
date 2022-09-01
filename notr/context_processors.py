from typing import Dict, Any

from .models import Notes, Labels, Comment
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from datetime import date
import calendar
my_date = date.today()

# @login_required()


def get_user_info(request):
    context = dict()

    try:
        query = request.GET.get('query', '')
        if request.user.is_authenticated:
            initial = f"{request.user.full_name.split(' ')[0][0]}"
            name = f"{request.user.full_name.split(' ')[0]}"
            context['initial'] = initial
            context['user_splited_name'] = name

        qs = Notes._normal_objects.filter(
            Q(owner_id=request.user.id) & Q(title__icontains=query))
        context['notes_list'] = qs.order_by('-is_pinned')
        context['archived'] = Notes._archived_objects.filter(
            Q(owner_id=request.user.id) & Q(title__icontains=query))
        context['trashed'] = Notes._trash_objects.filter(
            Q(owner_id=request.user.id) & Q(title__icontains=query))
        context['user_favorites'] = Notes._normal_objects.filter(
            Q(owner_id=request.user.id) & Q(is_favorite=True))
        context['user_labels'] = Labels.objects.filter(user_id=request.user.id)
        context['comments'] = Comment.objects.filter(user_id=request.user.id)
        context['day'] = calendar.day_name[my_date.weekday()]
        return context
    except Exception as e:
        print(e)
        return context
