from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.
from .models import User


class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'full_name',
                    'is_staff', "mobile", "is_verified"]
    search_fields = ('username', 'full_name',)
    ordering = ('email', )


admin.site.register(User)
