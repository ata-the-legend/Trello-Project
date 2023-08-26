from rest_framework import serializers
from trello.apps.dashboards.models import Label, Task

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ('__all__')


class TaskSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Task
        fields = ('__all__')