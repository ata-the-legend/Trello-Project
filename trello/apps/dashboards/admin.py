from django.contrib import admin
from .models import Attachment , Activity


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('file', 'task', 'owner')}),
    )
    list_display = ('owner', 'task', 'file')
    list_filter = ('is_active',)
    search_fields = ('task','owner')
    ordering = ('task',)




@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('doer', 'task', 'message')
    list_filter = ('message',)
    search_fields = ('doer', 'task',)
    ordering = ('task',)