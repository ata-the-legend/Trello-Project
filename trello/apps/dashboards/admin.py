from django.contrib import admin
from .models import Task, Comment, Label,Activity,Attachment

    
class ActivityInLine(admin.TabularInline):
    model = Activity
    readonly_fields = ['doer', 'message','task']
    can_delete = False
    max_num = 0


class AttachmentInLine(admin.TabularInline):
    model = Attachment


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
















