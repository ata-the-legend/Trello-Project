from rest_framework import serializers
from trello.apps.dashboards.models import Label, Task,Board

class LabelSerializer(serializers.Serializer):
    """
     Serializer for creating and updating labels.
    """
    title = serializers.CharField(max_length=300)
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    def create(self, validated_data):
        """
         Create a new label instance.
        """
        return Label.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing label instance.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.board = validated_data.get('board', instance.board)
        instance.save()
        return instance
    
class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for tasks.
    """
    
    class Meta:
        model = Task
        fields = ('__all__')