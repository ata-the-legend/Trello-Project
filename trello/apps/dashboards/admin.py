from django.contrib import admin
from .models import Attachment , Activity


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('file', 'task', 'owner')}),
    )
    list_display = ('file', 'task', 'owner')
    list_filter = ('task',)
    search_fields = ('file',)
    ordering = ('task',)




@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('doer', 'message', 'task')}),
    )
    list_display = ('doer', 'message', 'task')
    list_filter = ('task',)
    search_fields = ('message',)
    ordering = ('task',)