from rest_framework.viewsets import mixins, GenericViewSet
from trello.apps.dashboards.models import Comment
from trello.apps.dashboards.serializers import CommentSerializer
from trello.apps.dashboards.permissions import CommentPermission


class CommentViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    """
    This viewset allows creating, retrieving, updating, soft-deleting, and listing comments.
    Soft-deletion is performed using the 'SoftDestroyModelMixin' to archive comments
    instead of permanently deleting them.
    """
    queryset = Comment.objects.all().select_related('author')
    serializer_class = CommentSerializer
    permission_classes = [CommentPermission]

    def perform_destroy(self, instance):
        return instance.archive()