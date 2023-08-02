from django.db import models
from trello.apps.core.models import BaseModel
from trello.apps.accounts import User
from django.utils.translation import gettext as _


class WorkSpace(BaseModel):
    title = models.CharField(_("Title"), max_length=50, help_text='Title of the workspace')
    member = models.ForeignKey(User, verbose_name=_("Member"), on_delete=models.CASCADE, help_text='members of the workspace')
    owner = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.CASCADE, help_text='The owner of the workspace')


class Board(BaseModel):
    title = models.CharField(_("Title"), max_length=50, help_text='Title of the board')
    owner = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.CASCADE, help_text='The owner of the board')
    background_image = models.ImageField(_("Background image"), upload_to='uploads/photos/')


class List(BaseModel):
    title = models.CharField(_("Title"), max_length=50, help_text='Title of the list')
    board = models.ForeignKey(Board, verbose_name=_("Board"), on_delete=models.CASCADE, help_text='Board associated with the list')


class Task(BaseModel):
    title = models.CharField(max_length=300, verbose_name=_('Title'), help_text='Title of the task')
    description = models.TextField(verbose_name=_('Description'), help_text='Description of the task')
    status = models.CharField(max_length=300, verbose_name=_('Status'), help_text='Status of the task')
    order = models.IntegerField(verbose_name=_('Order'), help_text='Order of the task')
    label = models.ForeignKey('Label', on_delete=models.CASCADE, verbose_name=_('Label'), help_text='Label associated with the task')
    start_date = models.DateTimeField(verbose_name=_('Start Date'), help_text='Start date of the task')
    end_date = models.DateTimeField(verbose_name=_('End Date'), help_text='End date of the task')
    assigned_to = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name=_('Assigned To'), help_text='User assigned to the task')


class Label(BaseModel):
    title = models.CharField(max_length=300, verbose_name=_('Title'), help_text='Title of the label')
    board = models.ForeignKey('Board', on_delete=models.CASCADE, verbose_name=_('Board'), help_text='Board associated with the label')


class Comment(BaseModel):
    body = models.TextField(verbose_name=_('Body'), help_text='Body of the comment')
    task = models.ForeignKey('Task', on_delete=models.CASCADE, verbose_name=_('Task'), help_text='Task associated with the comment')
    author = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name=_('Author'), help_text='Author of the comment')
