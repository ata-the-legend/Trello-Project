from django.db import models
from trello.apps.core.models import BaseModel


class Task(BaseModel):
    title = models.CharField(max_length=300, verbose_name='Title', help_text='Title of the task')
    description = models.TextField(verbose_name='Description', help_text='Description of the task')
    status = models.CharField(max_length=300, verbose_name='Status', help_text='Status of the task')
    order = models.IntegerField(verbose_name='Order', help_text='Order of the task')
    label = models.ForeignKey('Label', on_delete=models.CASCADE, verbose_name='Label', help_text='Label associated with the task')
    start_date = models.DateTimeField(verbose_name='Start Date', help_text='Start date of the task')
    end_date = models.DateTimeField(verbose_name='End Date', help_text='End date of the task')
    assigned_to = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='Assigned To', help_text='User assigned to the task')


class Label(BaseModel):
    title = models.CharField(max_length=300, verbose_name='Title', help_text='Title of the label')
    board = models.ForeignKey('Board', on_delete=models.CASCADE, verbose_name='Board', help_text='Board associated with the label')


class Comment(BaseModel):
    body = models.TextField(verbose_name='Body', help_text='Body of the comment')
    task = models.ForeignKey('Task', on_delete=models.CASCADE, verbose_name='Task', help_text='Task associated with the comment')
    author = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='Author', help_text='Author of the comment')
