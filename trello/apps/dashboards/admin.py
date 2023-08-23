from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from .models import *
from .forms import MembersM2MAdminForm


class MembersInline(admin.TabularInline):
    model = WorkSpace.members.through
    form = MembersM2MAdminForm
    extra = 1
    raw_id_fields = ('user',)


class WorkSpaceBoardInline(admin.TabularInline):
    model = Board
    extra = 1


class BoardListInline(admin.TabularInline):
    model = TaskList
    extra = 1


class ListTaskInline(admin.TabularInline):
    model = Task
    extra = 1


@admin.register(WorkSpace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner']
    fields = ['title', 'owner', 'is_active']
    inlines = (MembersInline, WorkSpaceBoardInline)
    list_filter = ['is_active', 'title']

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
    list_filter = ['is_active', 'title']
    search_fields = ('title',)
    inlines = (BoardListInline,)


@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ['title', 'board']
    list_filter = ['is_active', 'title']
    search_fields = ('title',)
    inlines = (ListTaskInline,)


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


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'description', 'status')}),
        ('Dates', {'fields': ('start_date', 'end_date')}),
        ('Relations', {'fields': ('labels', 'assigned_to')}),
    )
    #inlines = [ActivityInLine, AttachmentInLine]
    list_display = ('title', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'labels', 'assigned_to', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    ordering = ('status', 'start_date')
    actions = ['archive_tasks']


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'board')}),
    )
    list_display = ('title', 'board')
    list_filter = ('board',)
    search_fields = ('title',)
    ordering = ('board',)