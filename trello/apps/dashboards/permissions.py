from rest_framework import permissions
from .models import TaskList, WorkSpace

class WorkspacePermissions(permissions.IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.members.all() or request.user == obj.owner
        elif request.method in ['POST', 'DELETE', 'PUT', 'PATCH',]:
            return request.user == obj.owner
        return False
    
class TaskPermissions(permissions.IsAuthenticated):

    # def has_permission(self, request, view):
    #     status = TaskList.objects.get(id=request.data['status'])
    #     workspace = WorkSpace.objects.get(id=status.board.work_space.id)
    #     return request.user in workspace.members.all() or request.user == workspace.owner

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS + ('POST', 'DELETE', 'PUT', 'PATCH',):
            return request.user in obj.status.board.work_space.members.all() or request.user == obj.status.board.work_space.owner
        
        return False


class AttachmentPermissions(permissions.IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.task.status.board.work_space.members.all() or request.user == obj.task.status.board.work_space.owner
        elif request.method in ['POST', 'DELETE', 'PUT', 'PATCH',]:
            return request.user == obj.owner or request.user == obj.task.status.board.work_space.owner

class BoardPermission(permissions.IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS + ('POST', 'PUT', 'PATCH',):
            return request.user in obj.work_space.members.all() or request.user == obj.work_space.owner
        elif request.method == 'DELETE':
            return request.user == obj.work_space.owner
        return False


class TaskListPermissions(permissions.IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS + ('POST', 'DELETE', 'PUT', 'PATCH',):
            return request.user in obj.board.work_space.members.all() or request.user == obj.board.work_space.owner
        

        return False


class LabelPermission(permissions.IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS + ('POST', 'DELETE', 'PUT', 'PATCH',):
            return request.user in obj.board.work_space.members.all() or request.user == obj.board.work_space.owner
        
        return False

