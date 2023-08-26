from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from .models import *
from .forms import MembersM2MAdminForm


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
    extra = 1
    raw_id_fields = ('user',)


class AssignToInline(admin.TabularInline):
    model = Task.assigned_to.through
    form = MembersM2MAdminForm
    extra = 1
    raw_id_fields = ('user',)

class WorkSpaceBoardInline(CustomTabularInline):
    model = Board
    extra = 1
    

class BoardListInline(CustomTabularInline):
    model = TaskList
    extra = 1



class ListTaskInline(CustomTabularInline):
    model = Task
    extra = 1
    # raw_id_fields = ('assigned_to', 'labels')
    # fields = ['title', 'description']
    readonly_fields = ['assigned_to', 'labels']


@admin.register(WorkSpace)
class WorkspaceAdmin(CustomModelAdmin):
    list_display = ['title', 'owner', 'is_active']
    fields = ['title', 'owner', 'is_active']
    inlines = (MembersInline, WorkSpaceBoardInline)
    list_filter = ['is_active']
    search_fields = ('title', 'owner__email',)
    raw_id_fields = ['owner']


@admin.register(Board)
class BoardAdmin(CustomModelAdmin):
    list_display = ['title', 'work_space', 'is_active']
    list_filter = ['is_active',]
    search_fields = ('title', 'work_space__title', 'work_space__owner__email',)
    inlines = (BoardListInline,)
    raw_id_fields = ('work_space',)



@admin.register(TaskList)
class TaskListAdmin(CustomModelAdmin):
    list_display = ['title', 'board', 'is_active']
    list_filter = ['is_active',]
    search_fields = ('title', 'board__work_space__title', 'board__work_space__owner__email')
    inlines = (ListTaskInline,)
    raw_id_fields = ('board',)


@admin.register(Attachment)
class AttachmentAdmin(CustomModelAdmin):
    fieldsets = (
        (None, {'fields': ('task', 'owner', 'file',)}),
    )
    list_display = ('owner', 'task', 'file', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('task__title','owner__email')
    ordering = ('task',)
    raw_id_fields = ('owner', 'task')



@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('doer', 'task', 'message', )
    list_filter = ('message',)
    search_fields = ('doer__email', 'task__status__board__work_space__title')
    ordering = ('task',)
    readonly_fields = ('doer', 'task', 'message', )



class TaskAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'description', 'status')}),
        ('Dates', {'fields': ('start_date', 'end_date')}),
        ('Relations', {'fields': ('labels', 'assigned_to')}),
    )
    inlines = [ActivityInLine, AttachmentInLine]
    list_display = ('title', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'labels', 'assigned_to', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    ordering = ('status', 'start_date')
    actions = ['archive_tasks']

admin.site.register(Task, TaskAdmin)
    

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('body', 'task', 'author')}),
        ('Status', {'fields': ('is_active',)}),
    )
    list_display = ('body', 'task', 'author')
    list_filter = ('task','author')
    search_fields = ('body',)
    ordering = ('task',)

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'board')}),
    )
    list_display = ('title', 'board')
    list_filter = ('board',)
    search_fields = ('title',)
    ordering = ('board',)
















