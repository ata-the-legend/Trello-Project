from rest_framework import permissions
from trello.apps.dashboards.models import *

class AttachmentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if view.action in ['list', 'retrieve']:
            attachment = view.get_object()
            workspace_members = attachment.task.status.board.work_space.members.all()
            return user in workspace_members
        elif view.action in ['create', 'update', 'destroy']:
            attachment = view.get_object()
            workspace_owner = attachment.task.status.board.work_space.owner
            return user == attachment.owner or user == workspace_owner
        return True
