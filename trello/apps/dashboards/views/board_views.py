from rest_framework.viewsets import GenericViewSet, mixins
from ..serializers import BoardSerializer
from ..models import Board

class BoardModelViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        GenericViewSet):

    serializer_class = BoardSerializer
    queryset = Board.objects.all().select_related('work_space').prefetch_related('board_Tasklists')
    permission_classes = []
    
    def perform_destroy(self, instance):
        instance.archive()