from rest_framework import viewsets,status
from trello.apps.dashboards.models import Comment
from trello.apps.dashboards.serializers import CommentSerializer
from rest_framework.response import Response

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.archive()
        return Response(status=status.HTTP_204_NO_CONTENT)