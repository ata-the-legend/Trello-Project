from rest_framework import viewsets
from ..models import WorkSpace
from ..serializers import WorkSpaceSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from trello.apps.accounts.permissions import UserPermission
from django.shortcuts import get_object_or_404

class WorkSpaceViewSet(viewsets.ViewSet):
    permission_classes = [UserPermission]
    serializer_class = WorkSpaceSerializer
    queryset = WorkSpace.objects.all()

    def list(self, request):
        serz_data = WorkSpaceSerializer(instance=self.queryset, many=True)
        return Response(data=serz_data.data)

    def create(self, request):
        srz_data = WorkSpaceSerializer(data=request.Post)
        if serz_data.is_valid():
            WorkSpace.objects.create(
                title=srz_data.validated_data['title'],
                members=srz_data.validated_data['members'],
                owner=srz_data.validated_data['owner'],
            )

    def retrieve(self, request, pk=None):
        workspace = get_object_or_404(self.queryset, pk=pk)
        serz_data = WorkSpaceSerializer(instance=workspace)
        return Response(data=serz_data.data)

    def update(self, request, pk=None):
        workspace = get_object_or_404(self.queryset, pk=pk)
        if workspace.owner != request.user:
            return Response({'permission denied':'you are not the owner.'})
        serz_data = WorkSpaceSerializer(instance=workspace, data=request.Post)
        if serz_data.is_valid():
            serz_data.save()
            return Response(data=serz_data.data)
        return Response(data=serz_data.errors)

    def partial_update(self, request, pk=None):
        workspace = get_object_or_404(self.queryset, pk=pk)
        if workspace.owner != request.user:
            return Response({'permission denied':'you are not the owner.'})
        serz_data = WorkSpaceSerializer(instance=workspace, data=request.Post, partial=True)
        if serz_data.is_valid():
            serz_data.save()
            return Response(data=serz_data.data)
        return Response(data=serz_data.errors)

    def destroy(self, request, pk=None):
        workspace = get_object_or_404(self.queryset, pk=pk)
        workspace.archive()
        workspace.save()
        return Response({"message":"work space deactivated."})
