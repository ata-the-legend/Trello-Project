from rest_framework import serializers
from trello.apps.dashboards.models import Label, Task,Board

class LabelSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=300)
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    def create(self, validated_data):
        return Label.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.board = validated_data.get('board', instance.board)
        instance.save()
        return instance
    
class TaskSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Task
        fields = ('__all__')