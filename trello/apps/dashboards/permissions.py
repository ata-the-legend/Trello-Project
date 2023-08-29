from rest_framework import permissions
from trello.apps.dashboards.models import *



class LabelPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['create', 'update', 'destroy']:
            user = request.user
            label = view.get_object()
            workspace_owner = label.board.work_space.owner
            return user == label.owner or user == workspace_owner
        return True


