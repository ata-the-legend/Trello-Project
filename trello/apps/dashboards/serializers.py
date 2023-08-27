from rest_framework import serializers
from trello.apps.dashboards.models import Comment

class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('author', 'task', 'parent')

    def create(self, validated_data):
        user = self.context['request'].user
        task = validated_data['task']
        parent = validated_data.get('parent')
        body = validated_data['body']
        comment = Comment.create_comment(body, task, user, parent)
        return comment
    

    def update(self, instance, validated_data):
        body = validated_data.get('body')
        instance.update_comment(body)
        return instance
    
    def destroy(self, instance):
        instance.archive()