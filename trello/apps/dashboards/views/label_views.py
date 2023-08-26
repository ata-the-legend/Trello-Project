from rest_framework import viewsets
from rest_framework.response import Response
from dashboards.serializers import LabelSerializer, TaskSerializer
from trello.apps.dashboards.models import Label


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    
    def create_label(self, request):
        title = request.data.get('title')
        board = request.data.get('board')
        label = Label.create_label(title, board)
        serializer = self.get_serializer(label)
        return Response(serializer.data)
    
    def get_label_choices(self, request):
        choices = Label.get_label_choices()
        return Response(choices)
    
    def get_tasks(self, request, pk=None):
        label = self.get_object()
        tasks = label.get_tasks()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    def get_task_count(self, request, pk=None):
        label = self.get_object()
        count = label.get_task_count()
        return Response({'count': count})