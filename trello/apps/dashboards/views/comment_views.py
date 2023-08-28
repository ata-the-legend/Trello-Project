from rest_framework import viewsets,status,mixins
from trello.apps.dashboards.models import Comment
from rest_framework.mixins import DestroyModelMixin
from trello.apps.dashboards.serializers import CommentSerializer
from rest_framework.response import Response



class SoftDestroyModelMixin:
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.archive()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CommentViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   SoftDestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


