from django.contrib import admin
from django.utils.translation import gettext_lazy as _ 
from .models import Task, Comment, Label


class CommentInLine(admin.TabularInline):
    model = Comment
    extra = 1

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields':('title','description', 'status', 'order', 'labels','start_date', 'end_date', 'assigned_to')}),(_('Permissions'),{'fields':('is_active',)}),
    )
    inlines = [CommentInLine]
    list_display = ('title','status','order','start_date','end_date')
    list_filter = ('status', 'labels','assigned_to')
    search_fields = ('title',)
    ordering = ('status', 'order')
    

