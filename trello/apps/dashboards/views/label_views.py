from rest_framework import viewsets ,status
from rest_framework.response import Response
from trello.apps.dashboards.serializers import LabelSerializer, TaskSerializer
from trello.apps.dashboards.models import Label


class LabelViewSet(viewsets.ModelViewSet):
 
    serializer_class = LabelSerializer
    queryset = Label.objects.all()