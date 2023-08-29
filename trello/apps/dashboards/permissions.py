from rest_framework import permissions

class CommentPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.task.status.board.work_space.members.all() or request.user == obj.task.status.board.work_space.owner
        elif request.method in ['POST', 'DELETE', 'PUT', 'PATCH']:
            return request.user == obj.author or request.user == obj.task.status.board.work_space.owner
        return False