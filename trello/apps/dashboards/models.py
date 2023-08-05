from django.conf import settings
from django.db import models
from trello.apps.core.models import BaseModel, SoftDeleteMixin
from django.utils.translation import gettext as _


class WorkSpace(BaseModel):
    title = models.CharField(_("Title"), max_length=150, help_text='Title of the workspace')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("Members"), help_text='members of the workspace', related_name='member_work_spaces')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Owner"), on_delete=models.CASCADE, help_text='The owner of the workspace', related_name='owner_work_spaces')


class Board(BaseModel):
    title = models.CharField(_("Title"), max_length=150, help_text='Title of the board')
    work_space = models.ForeignKey(WorkSpace, verbose_name=_("Owner"), on_delete=models.CASCADE, help_text='work space of the board', related_name='work_space_boards')
    background_image = models.ImageField(_("Background image"), upload_to='uploads/backgrounds/', default='uploads/backgrounds/default_background.jpg')


class List(BaseModel):
    title = models.CharField(_("Title"), max_length=150, help_text='Title of the list')
    board = models.ForeignKey(Board, verbose_name=_("Board"), on_delete=models.CASCADE, help_text='Board associated with the list', related_name='board_lists')



class Label(BaseModel, SoftDeleteMixin):
    title = models.CharField(max_length=300, verbose_name=_('Title'), help_text='Title of the label')
    board = models.ForeignKey(Board, on_delete=models.CASCADE, verbose_name=_('Board'), help_text='Board associated with the label', related_name='board_labels')
    
    class Meta:
        verbose_name = _('Label')
        verbose_name_plural =_("Labels")
    def __str__(self):
        return self.title

class Task(BaseModel, SoftDeleteMixin):
    title = models.CharField(max_length=300, verbose_name=_('Title'), help_text='Title of the task')
    description = models.TextField(verbose_name=_('Description'), help_text='Description of the task')
    status = models.ForeignKey(List ,verbose_name=_('Status'), on_delete=models.CASCADE, help_text='Status of the task', related_name='status_tasks')
    order = models.IntegerField(verbose_name=_('Order'), help_text='Order of the task')
    labels = models.ManyToManyField(Label, verbose_name=_('Label'), help_text='Label associated with the task', related_name='label_tasks')
    start_date = models.DateTimeField(verbose_name=_('Start Date'), help_text='Start date of the task', null=True, blank=True)
    end_date = models.DateTimeField(verbose_name=_('End Date'), help_text='End date of the task', null=True, blank=True)
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('Assigned To'), help_text='User assigned to the task', related_name='assigned_tasks')

    class Meta:
        verbose_name =_('Task')
        verbose_name_plural =_('Tasks')
    def __str__(self):
        return f'Task {self.title}'
    
class Comment(BaseModel, SoftDeleteMixin):
    body = models.TextField(verbose_name=_('Body'), help_text='Body of the comment')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name=_('Task'), help_text='Task associated with the comment', related_name='task_comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name=_('Author'), help_text='Author of the comment', related_name='author_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name=_('Parent'), null=True, blank=True)


    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural =_('Comments')

    def __str__(self):
        return f'Comment by {self.author} on task {self.task}'

class Attachment(BaseModel):
    file = models.FileField(verbose_name=_("file") , max_length=100 ,upload_to='uploads/attachments/' , blank=True)
    task = models.ForeignKey(Task,verbose_name=_('Task'), on_delete=models.CASCADE,  help_text='Task of the attachment', related_name='task_attachments')


    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural =_("Attachments")


    def __str__(self):
        return self.file


class Activity(BaseModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name=_('Author'), help_text='Author of the activity', related_name='author_activity')
    message = models.TextField(verbose_name=_('message'), max_length=300 , help_text='message of the activity')
    task = models.ForeignKey(Task,verbose_name=_('Task'), on_delete=models.CASCADE,  help_text='Task associated with the activity', related_name='task_activity')
    
    

    class Meta:
        verbose_name = _('Activitie')
        verbose_name_plural =_("Activities")
        ordering = ["create_at"]


    def __str__(self):
        return f'{self.author} activity'
