from django.conf import settings
from django.db import models
from trello.apps.core.models import BaseModel, SoftDeleteMixin
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist


class WorkSpace(BaseModel, SoftDeleteMixin):
    title = models.CharField(_("Title"), max_length=150, help_text='Title of the workspace')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("Members"), help_text='members of the workspace', related_name='member_work_spaces')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Owner"), on_delete=models.CASCADE, help_text='The owner of the workspace', related_name='owner_work_spaces')

    class Meta:
        verbose_name = _("Work Space")
        verbose_name_plural = _("Work Spaces")
        ordering = ["-create_at"]

    def __str__(self):
        return f'{self.title} - owned by {self.owner}'

    def add_member():
        pass

class Board(BaseModel, SoftDeleteMixin):
    title = models.CharField(_("Title"), max_length=150, help_text='Title of the board')
    work_space = models.ForeignKey(WorkSpace, verbose_name=_("Workspace"), on_delete=models.CASCADE, help_text='work space of the board', related_name='work_space_boards')
    background_image = models.ImageField(_("Background image"), upload_to='uploads/backgrounds/', default='uploads/backgrounds/default_background.jpg')

    class Meta:
        verbose_name = _("Board")
        verbose_name_plural = _("Boards")
        ordering = ["work_space"]

    def __str__(self):
        return f'{self.title} - related work space: {self.work_space}'

class TaskList(BaseModel, SoftDeleteMixin):
    title = models.CharField(_("Title"), max_length=150, help_text='Title of the Tasklist')
    board = models.ForeignKey(Board, verbose_name=_("Board"), on_delete=models.CASCADE, help_text='Board associated with the Tasklist', related_name='board_Tasklists')

    class Meta:
        verbose_name = _("TaskList")
        verbose_name_plural = _("TaskLists")
        ordering = ["board"]

    def __str__(self):
        return f'{self.title} - related board: {self.board}'


class Label(BaseModel):
    title = models.CharField(max_length=300, verbose_name=_('Title'), help_text='Title of the label')
    board = models.ForeignKey(Board, on_delete=models.CASCADE, verbose_name=_('Board'), help_text='Board associated with the label', related_name='board_labels')
    
    class Meta:
        verbose_name = _('Label')
        verbose_name_plural =_("Labels")

    def __str__(self):
        return self.title
    
    @classmethod
    def create_label(cls, title, board):
        label = cls.objects.create(title=title, board=board)
        return label
    
    @staticmethod
    def get_label_choices():
        return Label.objects.values_list('title',flat=True)

    @staticmethod
    def get_board_labels(board):
        return Label.objects.filter(board=board)
    
    def update_label(self, title=None):
        if title is not None:
            self.title = title
            self.save()

    def delete_label(self):

        self.delete()

    def get_tasks(self):
        return self.label_tasks.all()
    
    def get_task_count(self):
        return self.label_tasks.count()


class Task(BaseModel, SoftDeleteMixin):
    title = models.CharField(max_length=300, verbose_name=_('Title'), help_text='Title of the task')
    description = models.TextField(verbose_name=_('Description'), help_text='Description of the task')
    status = models.ForeignKey(TaskList ,verbose_name=_('Status'), on_delete=models.CASCADE, help_text='Status of the task', related_name='status_tasks')
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
    
    @classmethod
    def create_task(cls, title, description, status, order, labels=None, start_date=None, end_date=None, assigned_to=None):
        task = cls.objects.create(
            title=title,
            description=description,
            status=status,
            order=order,
            start_date=start_date,
            end_date=end_date,
        )
        if labels:
            task.labels.set(labels)
        if assigned_to:
            task.assigned_to.set(assigned_to)
        return task
    
    def update_task(self, title=None, description=None, status=None, order=None, labels=None,start_date=None, end_date=None, assigned_to=None):
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if status is not None:
            self.status = status
        if order is not None:
            self.order = order
        if start_date is not None:
            self.start_date = start_date
        if end_date is not None:
            self.end_date = end_date
        if labels is not None:
            self.labels.set(labels)
        if assigned_to is not None:
            self.assigned_to.set(assigned_to)
        self.save()

    def delete_task(self):
        try:
            self.delete()
        except ObjectDoesNotExist:
            pass

    def get_comment(self):
        return self.task_comments.all()
    
    def get_attachments(self):
        return self.task_attachments.all()
    
    def get_activity(self):
        return self.task_activity.all()
    
    def get_assigned_users(self):
        return self.assigned_to.all()
    
    @staticmethod
    def get_status_choices():
        return TaskList.objects.values_list('title', flat=True)
    
    @staticmethod
    def get_label_choices():
        return Label.objects.values_list('title',flat=True)
    
    @staticmethod
    def get_start_date_choices():
        return Task.objects.exclude(start_date=None).values_list('start_date',flat=True).distinct()
    
    @staticmethod
    def get_end_date_choices():
        return Task.objects.exclude(end_date=None).values_list('end_date',flat=True).distinct()


    
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

class Attachment(BaseModel , SoftDeleteMixin):
    file = models.FileField(verbose_name=_("file") , max_length=100 ,upload_to='uploads/attachments/' , blank=True)
    task = models.ForeignKey(Task,verbose_name=_('Task'), on_delete=models.CASCADE,  help_text='Task of the attachment', related_name='task_attachments')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Owner"), on_delete=models.DO_NOTHING, related_name='owner_attachments')

    @classmethod
    def create(cls, file, task, owner):
        attachment = cls.objects.create(file,task, owner)
        message = f"{owner.get_full_name()} attached a new file."
        Activity.objects.create(task, doer=owner, message = message)
        return attachment

    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural =_("Attachments")


    def __str__(self):
        return f"Attached by {self.owner.name}."


class Activity(BaseModel):

    doer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name=_('Doer'), help_text='Doer of the activity', related_name='doer_activity')
    message = models.TextField(verbose_name=_('message'), max_length=300 , help_text='message of the activity')
    task = models.ForeignKey(Task,verbose_name=_('Task'), on_delete=models.CASCADE,  help_text='Task associated with the activity', related_name='task_activity')
    
    class Meta:
        verbose_name = _('Activitie')
        verbose_name_plural =_("Activities")
        ordering = ["create_at"]


    def __str__(self):
        return f'{self.update_at} - {self.message}'
