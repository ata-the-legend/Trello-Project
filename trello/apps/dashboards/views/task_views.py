from rest_framework.viewsets import mixins, GenericViewSet
from ..permissions import TaskPermissions
from ..serializers import TaskSerializer
from ..models import Task



class TaskViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    
    permission_classes = [TaskPermissions,]
    queryset =  Task.objects.all().select_related('status').prefetch_related('labels')\
        .prefetch_related('assigned_to').prefetch_related('task_comments').prefetch_related('task_attachments')\
        .prefetch_related('task_activity')
    
    serializer_class = TaskSerializer

    def perform_destroy(self, instance):
        return instance.archive()