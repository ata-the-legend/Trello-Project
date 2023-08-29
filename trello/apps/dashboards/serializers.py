from rest_framework import serializers
from trello.apps.accounts.models import User
from .models import WorkSpace, Board


class WorkSpaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkSpace
        fields = ['title', 'members', 'owner',]


class WorkSpaceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSpace
        fields = ['id', 'title', 'owner', ]


class BoardSerializer(serializers.ModelSerializer):
    work_space = WorkSpaceListSerializer(read_only=True)
    board_Tasklists = WorkSpaceListSerializer(read_only=True, many=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'background_image', 'work_space', 'board_Tasklists', ]
        read_only_fields = ['id', 'work_space',]