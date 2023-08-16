from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
from rest_framework import mixins


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

# class RegisterModelMixin(mixins.CreateModelMixin):
#     def register(self, request, *args, **kwargs):
#         self.create(self, request, *args, **kwargs)



class UserView(SoftDestroyModelMixin, 
               ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
