from rest_framework import serializers
from trello.apps.accounts.models import User
from .models import Board, WorkSpace

class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'avatar', ]


class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'title','update_at', 'create_at', ]

class WorkspaceSerializer(serializers.ModelSerializer):
    work_space_boards = BoardListSerializer(many=True, read_only=True)
    owner = UserListSerializer(read_only=True)
    members = UserListSerializer(many=True, read_only=True)
    add_members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all().exclude(id=owner.data.get(id)), many=True, write_only=True)

    class Meta:
        model = WorkSpace
        exclude = ['is_active']
        read_only_fields = ['update_at', 'create_at']

    def create(self, validated_data):
        validated_data['members'] = validated_data.pop("add_members")
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        validated_data['owner'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if validated_data.get('add_members', None):
            validated_data['members'] = validated_data.pop("add_members")
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        validated_data['owner'] = user
        return super().update(instance, validated_data)

    def validate(self, attrs):
        if attrs.get('add_members', None):
            user = None
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                user = request.user
            if user in attrs['add_members']:
                attrs['add_members'].remove(user)
        return super().validate(attrs)
    
class WorkspaceAddMemberSerializer(serializers.Serializer):
    new_members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

