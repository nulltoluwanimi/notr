from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import Notes, Comment, Labels
# Register your models here.


class ProjectAdmin(GuardedModelAdmin):
    pass


class LabelsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'user')


admin.site.register(Notes)
admin.site.register(Labels, LabelsAdmin)
admin.site.register(Comment)
