from typing import Any, Optional
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from trello.apps.accounts.models import User
from .models import *
from .forms import MembersM2MAdminForm
from django.utils.translation import gettext_lazy as _
from django.db.models import Q


class CustomModelAdmin(admin.ModelAdmin):
    
    actions = ['archive', 'restore']

    @admin.action(description=f'Archive Selected Items')
    def archive(self, request, queryset):
        queryset.archive()
        

    @admin.action(description='Restore Selected Items')
    def restore(self, request, queryset):
        queryset.restore()

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = self.model.original_objects.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
    

class CustomTabularInline(admin.TabularInline):

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = self.model.original_objects.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

class MembersInline(admin.TabularInline):
    model = WorkSpace.members.through
    form = MembersM2MAdminForm
    extra = 0
    raw_id_fields = ('user',)


class WorkSpaceBoardInline(CustomTabularInline):
    model = Board
    extra = 0
    

class BoardListInline(CustomTabularInline):
    model = TaskList
    extra = 0



class ListTaskInline(CustomTabularInline):
    model = Task
    extra = 0
    # raw_id_fields = ('assigned_to', 'labels')
    # fields = ['title', 'description']
    readonly_fields = ['assigned_to', 'labels']

class ActivityInLine(admin.TabularInline):
    model = Activity
    extra = 0
    readonly_fields = ('doer', 'message', "create_at")
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class AttachmentInLine(CustomTabularInline):
    model = Attachment
    extra = 0
    raw_id_fields = ('owner',)


@admin.register(WorkSpace)
class WorkspaceAdmin(CustomModelAdmin):
    fieldsets = (
        (None, {'fields': ('id', 'title', 'owner', 'is_active',)}),
        (_("Important dates"), {"fields": ("create_at", "update_at")})
    )
    list_display = ['title', 'owner', 'is_active']
    inlines = (MembersInline, WorkSpaceBoardInline)
    list_filter = ['is_active']
    search_fields = ('title', 'owner__email',)
    raw_id_fields = ['owner']
    readonly_fields = ("create_at", "update_at", 'id')


@admin.register(Board)
class BoardAdmin(CustomModelAdmin):
    fieldsets = (
        (None, {'fields': ('id', 'title', 'work_space', 'background_image', 'is_active',)}),
        (_("Important dates"), {"fields": ("create_at", "update_at")})
    )
    list_display = ['title', 'work_space', 'is_active']
    list_filter = ['is_active',]
    search_fields = ('title', 'work_space__title', 'work_space__owner__email',)
    inlines = (BoardListInline,)
    raw_id_fields = ('work_space',)
    readonly_fields = ("create_at", "update_at", 'id')



@admin.register(TaskList)
class TaskListAdmin(CustomModelAdmin):
    fieldsets = (
        (None, {'fields': ('id', 'title', 'board', 'is_active',)}),
        (_("Important dates"), {"fields": ("create_at", "update_at")})
    )
    list_display = ['title', 'board', 'is_active']
    list_filter = ['is_active',]
    search_fields = ('title', 'board__work_space__title', 'board__work_space__owner__email')
    inlines = (ListTaskInline,)
    raw_id_fields = ('board',)
    readonly_fields = ("create_at", "update_at", 'id')



@admin.register(Attachment)
class AttachmentAdmin(CustomModelAdmin):
    fieldsets = (
        (None, {'fields': ('id', 'task', 'owner', 'file', 'is_active',)}),
        (_("Important dates"), {"fields": ("create_at", "update_at")})
    )
    list_display = ('owner', 'task', 'file', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('task__title','owner__email')
    ordering = ('task',)
    raw_id_fields = ('owner', 'task')
    readonly_fields = ("create_at", "update_at", 'id')



@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('id', 'message', 'task', 'doer', )}),
        (_("Important dates"), {"fields": ("create_at",)})
    )
    list_display = ('doer', 'task', 'message', )
    list_filter = ('message',)
    search_fields = ('doer__email', 'task__status__board__work_space__title')
    ordering = ('task',)
    readonly_fields = ('message', 'task', 'doer', "create_at", 'id')
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Task)
class TaskAdmin(CustomModelAdmin):
    fieldsets = (
        (None, {'fields': ('id', 'title', 'description', 'status')}),
        ('Relations', {'fields': ('labels', 'assigned_to')}),
        ('Dates', {'fields': ('start_date', 'end_date', "create_at", "update_at")}),
    )
    inlines = [AttachmentInLine, ActivityInLine]
    list_display = ('title', 'status', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('status__title', 'status__board__title', 'status__board__work_space__title')
    readonly_fields = ("create_at", "update_at", 'id')

    def get_form(self, request: Any, obj: Any | None = ..., change: bool = ..., **kwargs: Any) -> Any:
        form = super().get_form(request, obj, change, **kwargs)
        if obj:
            form.base_fields['labels'].queryset = Label.objects.filter(board=obj.status.board)
            form.base_fields['status'].queryset = TaskList.objects.filter(board=obj.status.board)
            form.base_fields['assigned_to'].queryset =\
                User.objects.filter(Q(member_work_spaces=obj.status.board.work_space)\
                                    | Q(owner_work_spaces=obj.status.board.work_space))
        return form

    

@admin.register(Comment)
class CommentAdmin(CustomModelAdmin):
    fieldsets = (
        (None, {'fields': ('id', 'task', 'author', 'parent', 'body', 'is_active',)}),
        (_("Important dates"), {"fields": ("create_at", "update_at")}),
    )
    list_display = ('task', 'author', 'body', )
    list_filter = ('is_active',)
    search_fields = ('body', 'task__title','author__email')
    readonly_fields = ("create_at", "update_at", 'id')

    def get_form(self, request: Any, obj: Any | None = ..., change: bool = ..., **kwargs: Any) -> Any:
        form = super().get_form(request, obj, change, **kwargs)
        if obj:
            form.base_fields['task'].queryset = Task.objects.filter(status__board=obj.task.status.board)
            form.base_fields['parent'].queryset = Comment.objects.filter(task=obj.task)
            form.base_fields['author'].queryset =\
                User.objects.filter(Q(member_work_spaces=obj.task.status.board.work_space)\
                                    | Q(owner_work_spaces=obj.task.status.board.work_space))
        return form


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('id', 'title', 'board')}),
        (_("Important dates"), {"fields": ("create_at", "update_at")}),
    )
    list_display = ('title', 'board')
    search_fields = ('title', 'board__work_space__title', 'board__title')
    readonly_fields = ("create_at", "update_at", 'id')

    def get_form(self, request: Any, obj: Any | None = ..., change: bool = ..., **kwargs: Any) -> Any:
        form = super().get_form(request, obj, change, **kwargs)
        if obj:
            form.base_fields['board'].queryset = Board.objects.filter(work_space=obj.board.work_space)
        return form






