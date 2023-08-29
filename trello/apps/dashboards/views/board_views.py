from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from ..permissions import BoardPermission
from ..serializers import BoardSerializer
from ..models import Board, TaskList, Label

class BoardModelViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        GenericViewSet):

    serializer_class = BoardSerializer
    queryset = Board.objects.all().select_related('work_space').prefetch_related('board_Tasklists')
    permission_classes = [BoardPermission]
    
    def perform_destroy(self, instance):
        return instance.archive()

    @action(detail=True)
    def get_status_choices(self, request, pk=None):
        board = self.get_object()
        query = TaskList.objects.filter(board=board)
        serializer = self.get_serializer(query, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def get_board_labels(self, request, pk=None):
        board = self.get_object()
        query = Label.objects.filter(board=board)
        serializer = self.get_serializer(query, many=True)
        return Response(serializer.data)