from rest_framework import serializers
from trello.apps.dashboards.models import Label

class LabelSerializer(serializers.ModelSerializer):
    """
     Serializer for creating and updating labels.
    """
    class Meta:
        model = Label
        fields = ('__all__')
        read_only_fields = ['update_at', 'create_at']

    