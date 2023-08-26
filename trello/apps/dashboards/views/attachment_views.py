from rest_framework import viewsets
from trello.apps.dashboards.models import Attachment
from trello.apps.dashboards.serializers import AttachmentSerializer

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    