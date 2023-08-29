from rest_framework import permissions



class LabelPermission(permissions.IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS + ('POST', 'DELETE', 'PUT', 'PATCH',):
            return request.user in obj.board.work_space.members.all() or request.user == obj.board.work_space.owner
        
        return False