from rest_framework import permissions
from trello.apps.dashboards.models import *



class LabelPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if view.action in ['list', 'retrieve']:
            label = view.get_object()
            workspace_members = label.board.work_space.members.all()
            return user in workspace_members
        elif view.action in ['create', 'update', 'destroy']:
            label = view.get_object()
            workspace_owner = label.board.work_space.owner
            return user == label.owner or user == workspace_owner
        return True