from rest_framework import permissions

class WorkspacePermissions(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.members.all() or request.user == obj.owner
        elif request.method in ['POST', 'DELETE', 'PUT', 'PATCH',]:
            return request.user == obj.owner
        return False
