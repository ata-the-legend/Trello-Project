from rest_framework import permissions


class BoardPermission(permissions.IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS + ('POST', 'PUT', 'PATCH',):
            return request.user in obj.work_space.members.all() or request.user == obj.work_space.owner
        elif request.method == 'DELETE':
            return request.user == obj.work_space.owner
        return False
