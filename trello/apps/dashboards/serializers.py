from rest_framework import serializers
from .models import Attachment
from trello.apps.accounts.serializers import UserListSerializer###########


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for handling task attachments.
    """
    # file = serializers.FileField()
    # task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    owner = UserListSerializer(read_only=True)


    class Meta:
        model = Attachment
        exclude = ['is_active']
        read_only_fields = ['update_at', 'create_at']
        extra_kwargs = {
            'file': {'required': True},
        }

    def create(self,validated_data):
        """
        Create a new attachment instance.
        """
        file = validated_data.get('file')
        task = validated_data.get('task')
        owner = self.context['request'].user
        attachment = Attachment.create(file, task, owner)
        return attachment
    

    def update(self, instance, validated_data):
        """
        Update an existing attachment instance.
        """
        instance.file = validated_data.get('file', instance.file)
        instance.task = validated_data.get('task',instance.task)
        instance.save()
        return instance
    