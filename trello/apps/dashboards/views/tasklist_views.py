from rest_framework import viewsets
from ..serializers import TaskListSerializer
from ..models import TaskList

class TaskListModelViewSet(viewsets.ModelViewSet):
    serializer_class = TaskListSerializer
    queryset = TaskList.objects.all()
    permission_classes = []
    
    def perform_destroy(self, instance):
        instance.archive()