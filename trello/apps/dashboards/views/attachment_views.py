from rest_framework import viewsets , status, mixins
from rest_framework.mixins import DestroyModelMixin
from trello.apps.dashboards.models import Attachment
from trello.apps.dashboards.serializers import AttachmentSerializer
from rest_framework.response import Response


class SoftDestroyModelMixin(DestroyModelMixin):
     def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.archive()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AttachmentViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        SoftDestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    