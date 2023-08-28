from rest_framework import serializers
from trello.apps.dashboards.models import Comment

class CommentSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False)
   


    class Meta:
        model = Comment
        fields = ['id', 'body', 'task', 'author', 'parent']
        read_only_fields = ['id', 'task', 'author']

    def create(self, validated_data):
        
        task = self.context.get('task') 
        author = self.context['request'].user
        parent = validated_data.get('parent')
        comment = Comment.create_comment(body=validated_data['body'], task=task, author=author, parent=parent)
        return comment

    def update(self, instance, validated_data):
        body = validated_data.get('body')
        instance.update_comment(body)
        return instance