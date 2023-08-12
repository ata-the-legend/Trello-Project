from typing import Any, Optional
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return
        qs.filter(assigned_to=request.user)

    def has_view_permission(self, request, obj = None):
        if not obj:
            return True
        if request.user.is_superuser:
            return True
        return obj.assigned_to.filter(pk=request.user.pk).exists()
    

    def has_change_permission(self, request, obj = None):
        if not obj:
            return True
        if request.user.is_superuser:
            return True
        return obj.assigned_to.filter(pk=request.user.pk).exists()
    

    def has_delete_permission(self, request, obj = None):
        if not obj:
            return True
        if request.user.is_superuser:
            return True
        return obj.assigned_to.filter(pk=request.user.pk).exists()
    

    @admin.register(Comment)
    class CommentAdmin(admin.ModelAdmin):
        fieldsets = (
            (None, {'fields':('body','task','author')}),
            (_('Permissions'),{'fields':('is_active',)}),
        )
        list_display = ('body', 'task', 'author')
        list_filter = ('task',)
        search_fields = ('body',)
        ordering = ('task',)


    @admin.register(Label)
    class LabelAdmin(admin.ModelAdmin):
        fieldsets = (
            (None,{'fields': ('title', 'board')}),
        )
        list_display = ('title','board')
        list_filter = ('board')
        search_fields = ('title',)
        ordering = ('board',)


