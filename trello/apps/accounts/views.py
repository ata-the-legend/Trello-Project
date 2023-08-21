from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserPasswordSerializer
from .permissions import UserPermission
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


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



class UserApiView(SoftDestroyModelMixin, 
               ModelViewSet):
    
    permission_classes = [UserPermission, ]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def change_password(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserPasswordSerializer(data=request.data)
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

