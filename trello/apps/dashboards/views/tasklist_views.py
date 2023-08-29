from rest_framework.viewsets import GenericViewSet, mixins
from ..serializers import TaskListSerializer
from ..models import TaskList
from ..permissions import TaskListPermissions

class TaskListModelViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        GenericViewSet):

    serializer_class = TaskListSerializer
    queryset = TaskList.objects.all().select_related('board').prefetch_related('status_tasks')
    permission_classes = [TaskListPermissions]
    
    def perform_destroy(self, instance):
        return instance.archive()