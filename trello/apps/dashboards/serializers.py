from rest_framework import serializers
from trello.apps.dashboards.models import Attachment



class AttachmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    owner = serializers.ReadOnlyField(source='owner.get_full_name')


    class Meta:
        model = Attachment
        fields = ['id','file','task','owner']



    def create(self,validated_data):
        file = validated_data.get('file')
        task = validated_data.get('task')
        owner = self.context['request'].user
        attachment = Attachment.create(file, task, owner)
        return attachment
    

    def update(self, instance, validated_data):
        instance.file = validated_data.get('file', instance.file)
        instance.task = validated_data.get('task',instance.task)
        instance.save()
        return instance
    
    def destroy(self, instance):
        instance.archive()