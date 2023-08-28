from rest_framework import viewsets
from ..serializers import BoardSerializer
from ..models import Board

class BoardModelViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    queryset = Board.objects.all()
    permission_classes = []
    
    def perform_destroy(self, instance):
        instance.archive()

