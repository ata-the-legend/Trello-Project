from rest_framework import viewsets, mixins
from trello.apps.dashboards.models import Attachment
from trello.apps.dashboards.serializers import AttachmentSerializer
from trello.apps.dashboards.permissions import AttachmentPermissions


class AttachmentViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """
    This viewset allows creating, retrieving, updating, and soft-deleting attachments.
    Soft-deletion is performed using the 'SoftDestroyModelMixin' to archive attachments
    instead of permanently deleting them.

    """
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [AttachmentPermissions]

    def perform_destroy(self, instance):
        return instance.archive()
    