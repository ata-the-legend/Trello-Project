from rest_framework import serializers
from rest_framework.fields import empty
from trello.apps.dashboards.models import Attachment,Task
from trello.apps.accounts.serializers import UserListSerializer


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for handling task attachments.
    """
    file = serializers.FileField()
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    owner = UserListSerializer()


    class Meta:
        model = Attachment
        fields = ['id','file','task','owner']

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
    