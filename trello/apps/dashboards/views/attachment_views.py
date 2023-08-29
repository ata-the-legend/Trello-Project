from rest_framework import viewsets , status, mixins
from rest_framework.mixins import DestroyModelMixin
from trello.apps.dashboards.models import Attachment
from trello.apps.dashboards.serializers import AttachmentSerializer
from rest_framework.response import Response
from rest_framework import permissions
from trello.apps.dashboards.permissions import AttachmentPermission


class SoftDestroyModelMixin:
     """
      Mixin for soft-deleting model instances.
     """
     def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.archive()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AttachmentViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        SoftDestroyModelMixin,
                        viewsets.GenericViewSet):
    """
    This viewset allows creating, retrieving, updating, and soft-deleting attachments.
    Soft-deletion is performed using the 'SoftDestroyModelMixin' to archive attachments
    instead of permanently deleting them.

    """
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated, AttachmentPermission]
    