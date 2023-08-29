from rest_framework import permissions


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve', 'update', 'partial_update', 'softdestroy', 'change_password']:
            return request.user and request.user.is_authenticated 
        elif view.action == 'create':
            return True
        else:
            return False
                                                                                                
    def has_object_permission(self, request, view, obj):
        # Deny actions on objects if the user is not authenticated
        if not request.user.is_authenticated:
            return False

        if view.action in ['retrieve', 'update', 'partial_update', 'softdestroy', 'change_password']:
            return obj == request.user
        else:
            return False
