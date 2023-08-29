from rest_framework import viewsets ,status
from rest_framework.response import Response
from trello.apps.dashboards.serializers import LabelSerializer, TaskSerializer
from trello.apps.dashboards.models import Label
from rest_framework import permissions
from trello.apps.dashboards.permissions import LabelPermission


class LabelViewSet(viewsets.ModelViewSet):
    """
    This viewset provides CRUD operations for managing labels. It supports creating,
    retrieving, updating, and deleting labels.
    """
 
    serializer_class = LabelSerializer
    queryset = Label.objects.all()
    permission_classes = [permissions.IsAuthenticated, LabelPermission]