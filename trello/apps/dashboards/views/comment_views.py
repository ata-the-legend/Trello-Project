from rest_framework import viewsets,status,mixins
from trello.apps.dashboards.models import Comment
from rest_framework.mixins import DestroyModelMixin
from trello.apps.dashboards.serializers import CommentSerializer
from rest_framework.response import Response
from rest_framework import permissions
from trello.apps.dashboards.permissions import CommentPermission


# class SoftDestroyModelMixin:
#     """
#     Mixin for soft-deleting model instances
#     """
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         instance.archive()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    
class CommentViewSet(viewsets.ModelViewSet):
    """
    This viewset allows creating, retrieving, updating, soft-deleting, and listing comments.
    Soft-deletion is performed using the 'SoftDestroyModelMixin' to archive comments
    instead of permanently deleting them.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    # permission_classes = [permissions.IsAuthenticated, CommentPermission]

    def perform_destroy(self, instance):
        return instance.archive()