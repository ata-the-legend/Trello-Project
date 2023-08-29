from rest_framework.viewsets import mixins, GenericViewSet
from rest_framework import status, filters
from rest_framework.response import Response
from .paginations import UserResultsSetPagination
from .models import User
from .serializers import UserListSerializer, UserSerializer, UserPasswordSerializer, WorkSpace
from .permissions import UserPermission
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from django.db.models import Prefetch


class SoftDestroyModelMixin:
    """
    Archive a model instance.
    """
    def softdestroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.archive()



class UserViewSet(SoftDestroyModelMixin, 
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    """
        User Crud ViewSet.
    """
    
    permission_classes = [UserPermission, ]
    queryset = User.objects.all().prefetch_related(
        Prefetch(
            'owner_work_spaces', 
            queryset=WorkSpace.objects.prefetch_related('members')
            )
        )
    
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['^first_name', '^last_name', '^email']
    ordering_fields = ['email', 'first_name', 'last_name',]
    ordering = ['email']
    pagination_class = UserResultsSetPagination

    def get_serializer_class(self):
        match self.action:
            case  'change_password':
                return UserPasswordSerializer
            case 'list':
                return UserListSerializer
        return super().get_serializer_class()

    @extend_schema(responses={'200': {'status': 'password set'}})
    @action(methods=['post'], detail=True, url_path='change-password')
    def change_password(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])
            user.save()
            tokens = OutstandingToken.objects.filter(user_id=request.user.id)
            for token in tokens:
                t, _ = BlacklistedToken.objects.get_or_create(token=token)
            return Response({'status': 'password set'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

