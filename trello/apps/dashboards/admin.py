from django.contrib import admin
from .models import WorkSpace, Board, Attachment , Activity
from .forms import MembersM2MAdminForm


class MembersInline(admin.TabularInline):
    model = WorkSpace.members.through
    form = MembersM2MAdminForm
    extra = 1
    raw_id_fields = ('user',)


@admin.register(WorkSpace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner']
    fields = ['title', 'owner']
    inlines = (MembersInline,)

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['work_space', 'title', 'background_image']


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
