from rest_framework import viewsets , status, mixins
from trello.apps.dashboards.models import Attachment
from trello.apps.dashboards.serializers import AttachmentSerializer
from rest_framework.response import Response


class AttachmentViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.archive()
        return Response(status=status.HTTP_204_NO_CONTENT)