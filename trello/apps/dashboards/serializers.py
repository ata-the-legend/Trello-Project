from rest_framework import serializers
from trello.apps.accounts.models import User
from .models import Activity, Attachment, Board, Comment, Label, Task, TaskList, WorkSpace
import traceback
from rest_framework.utils import model_meta
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

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
    add_members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        many=True, 
        write_only=True
    )

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


class TaskListListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskList
        fields = ["id", 'title']

class LabelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["id", 'title']

class CommentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ['is_active']

class AttachmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        exclude = ['is_active']

class ActivityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):

    obj_status = TaskListListSerializer(read_only=True, source='status')
    obj_labels = LabelListSerializer(many=True, read_only=True, source='labels')
    labels=serializers.PrimaryKeyRelatedField(queryset=Label.objects.all(), many=True, write_only=True)
    obj_assigned_to = UserListSerializer(many=True, read_only=True, source='assigned_to')
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, write_only=True)
    task_comments = CommentListSerializer(many=True, read_only=True)
    task_attachments = AttachmentListSerializer(many=True, read_only=True)
    task_activity = ActivityListSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        exclude = ['is_active']
        read_only_fields = ['update_at', 'create_at']
        extra_kwargs = {
            'description': {'required': False},
            'status': {'write_only':True},
        }
        
    def validate(self, attrs):
        attrs = super().validate(attrs)
        print(self.instance)
        if self.instance is not None:
            status = self.instance.status
        else:
            status = attrs['status']
        assigns = attrs['assigned_to']
        team_qs = status.board.work_space.work_space_members()
        team_owner = User.objects.get(id=status.board.work_space.owner.id)
        try:
            for user in assigns:
                if not team_owner == user:
                    team_qs.get(id=user.id)
        except ObjectDoesNotExist:
            raise ValidationError('User is not in workspace team')
        return attrs

    def _user(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        
    def create(self, validated_data):
        """
        We have a bit of extra checking around this in order to provide
        descriptive messages when something goes wrong, but this method is
        essentially just:

            return ExampleModel.objects.create(**validated_data)

        If there are many to many fields present on the instance then they
        cannot be set until the model is instantiated, in which case the
        implementation is like so:

            example_relationship = validated_data.pop('example_relationship')
            instance = ExampleModel.objects.create(**validated_data)
            instance.example_relationship = example_relationship
            return instance

        The default implementation also does not handle nested relationships.
        If you want to support writable nested relationships you'll need
        to write an explicit `.create()` method.
        """
        serializers.raise_errors_on_nested_writes('create', self, validated_data)

        ModelClass = self.Meta.model
        doer = self._user()

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass.create_task(**validated_data, doer=doer)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                'Got a `TypeError` when calling `%s.%s.create()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.%s.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception was:\n %s' %
                (
                    ModelClass.__name__,
                    ModelClass._default_manager.name,
                    ModelClass.__name__,
                    ModelClass._default_manager.name,
                    self.__class__.__name__,
                    tb
                )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)

        return instance

    def update(self, instance, validated_data):
        serializers.raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)
        doer = self._user()

        instance.update_task(doer=doer, **validated_data)

        return instance
    
