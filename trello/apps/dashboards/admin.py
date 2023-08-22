from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
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
    fields = ['title', 'owner', 'is_active']
    inlines = (MembersInline,)
    list_filter = ['is_active']

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = self.model.original_objects.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

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

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = self.model.original_objects.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('doer', 'task', 'message')
    list_filter = ('message',)
    search_fields = ('doer', 'task',)
    ordering = ('task',)
