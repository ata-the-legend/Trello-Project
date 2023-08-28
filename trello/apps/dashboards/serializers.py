from rest_framework import serializers
from .models import WorkSpace, Board


class WorkSpaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkSpace
        fields = ['title', 'members', 'owner']


class BoardSerializer(serializers.ModelSerializer):
    work_space = WorkSpaceSerializer()

    class Meta:
        model = Board
        fields = ['title', 'background_image', 'work_space']

    def create(self, validated_data):
        workspace_data = validated_data.pop('work_space')
        board = Board.objects.create(**validated_data)
        WorkSpace.objects.create(board=board, **workspace_data)
        return board

    def update(self, instance, validated_data):
        workspace_data = validated_data.pop('work_space')
        work_space = instance.work_space

        instance.title = validated_data.get('title', instance.title)
        instance.background_image = validated_data.get('background_image', instance.background_image)
        instance.save()

        return instance    