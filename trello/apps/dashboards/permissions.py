from rest_framework import permissions

class CommentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if view.action in ['list', 'retrieve']:
            comment = view.get_object()
            workspace_members = comment.task.status.board.work_space.members.all()
            return user in workspace_members
        elif view.action in ['create', 'update', 'destroy']:
            comment = view.get_object()
            workspace_owner = comment.task.status.board.work_space.owner
            return user == comment.author or user == workspace_owner
        return True
