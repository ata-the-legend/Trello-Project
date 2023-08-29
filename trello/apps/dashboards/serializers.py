from rest_framework import serializers
from trello.apps.dashboards.models import Comment

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating comments.
    """
    
   


    class Meta:
        model = Comment
        exclude =('is_active',)


    def create(self, validated_data):
        """
        Create a new comment instance.
        """
        author = self.context['request'].user 
        task = validated_data['task']
        body = validated_data['body']
        parent = validated_data.get('parent', None)
        comment = Comment.create_comment(body=body, task=task, author=author, parent=parent)
        return comment

    def update(self, instance, validated_data):
        """
        Update an existing comment instance.
        """
        body = validated_data.get('body', instance.body)
        instance.update_comment(body=body)
        return instance