from rest_framework import viewsets
from trello.apps.dashboards.models import Comment
from trello.apps.dashboards.serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


   