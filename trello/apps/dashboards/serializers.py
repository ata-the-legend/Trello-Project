from rest_framework import serializers
from .models import WorkSpace


class WorkSpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSpace
        fields = '__all__'
        read_only_fields = ['owner']