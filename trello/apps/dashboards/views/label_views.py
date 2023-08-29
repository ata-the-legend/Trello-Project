from rest_framework.viewsets import GenericViewSet, mixins
from trello.apps.dashboards.serializers import LabelSerializer
from trello.apps.dashboards.models import Label
from trello.apps.dashboards.permissions import LabelPermission


class LabelViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    """
    This viewset provides CRUD operations for managing labels. It supports creating,
    retrieving, updating, and deleting labels.
    """
 
    serializer_class = LabelSerializer
    queryset = Label.objects.all()
    permission_classes = [LabelPermission]