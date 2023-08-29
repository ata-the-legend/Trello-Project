from rest_framework import serializers
from trello.apps.accounts.models import User
from .models import WorkSpace, Board, TaskList


class WorkSpaceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSpace
        fields = [
            'id', 
            'title', 
            'owner', 
            ]


class TaskListListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskList
        fields = [
            'id', 
            'title', 
            ]


class BoardSerializer(serializers.ModelSerializer):
    board_work_space = WorkSpaceListSerializer(read_only=True, source='work_space')
    board_Tasklists = TaskListListSerializer(read_only=True, many=True)

    class Meta:
        model = Board
        fields = [
            'id', 
            'title', 
            'board_work_space', 
            'background_image', 
            'work_space', 
            'board_Tasklists', 
            ]
        extra_kwargs = {
            'work_space': {'write_only':True}
        }