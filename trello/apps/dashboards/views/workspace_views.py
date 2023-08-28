from rest_framework.viewsets import mixins, GenericViewSet
from ..serializers import WorkspaceAddMemberSerializer, WorkspaceSerializer
from ..models import WorkSpace
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema



class WorkspaceViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    
    queryset = WorkSpace.objects.all().prefetch_related('work_space_boards')
    serializer_class = WorkspaceSerializer

    def perform_destroy(self, instance):
        return instance.archive()

    @extend_schema(request=WorkspaceAddMemberSerializer, responses=WorkspaceAddMemberSerializer)
    @action(methods=['post'],detail=True, url_path='add-members')
    def add_members(self, request, *args, **kwargs):
        workspace = self.get_object()
        serializer = WorkspaceAddMemberSerializer(data=request.data)
        if serializer.is_valid():
            for member in serializer.validated_data['new_members']:
                if request.user == member:
                    continue
                workspace.add_member(member)
            workspace.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


