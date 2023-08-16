from django.conf import settings
from django.db import models
from trello.apps.core.models import BaseModel, SoftDeleteMixin
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError


class WorkSpace(BaseModel, SoftDeleteMixin):
    title = models.CharField(_("Title"), max_length=150, help_text='Title of the workspace')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("Members"), help_text='members of the workspace', related_name='member_work_spaces')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Owner"), on_delete=models.CASCADE, help_text='The owner of the workspace', related_name='owner_work_spaces')

    class Meta:
        verbose_name = _("WorkSpace")
        verbose_name_plural = _("WorkSpaces")
        ordering = ["-create_at"]

    def __str__(self):
        return f'{self.title} - owned by {self.owner}'

    def add_member(self, member):
        self.members.add(member)

    def add_board(self, title, background_image):
        if background_image is None:
            return Board.objects.create(title=title, work_space=self)
        return Board.objects.create(title=title, work_space=self, background_image=background_image)

    def work_space_members(self):
        return self.members.all() | settings.AUTH_USER_MODEL.objects.filter(owner=self.owner)
    
    def archive(self):
        board_qs = self.work_space_boards.all()
        list_qs = TaskList.objects.filter(board__in = board_qs)
        task_qs = Task.objects.filter(status__in = list_qs)
        task_qs.archive()
        list_qs.archive()
        board_qs.archive()
        return super().archive()
    
    def restore(self):
        board_qs = self.work_space_boards(manager = 'original_objects').all()
        list_qs = TaskList.original_objects.filter(board__in = board_qs)
        task_qs = Task.original_objects.filter(status__in = list_qs)
        task_qs.restore()
        list_qs.restore()
        board_qs.restore()
        return super().restore()
    
    def clean(self) -> None:
        if self.owner in self.members.all():
            raise ValidationError('Owner cant be member')
        return super().clean()


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

    def add_tasklist(self, title):
        return self.board_Tasklists.create(title=title)
    
    def get_board_labels(self):
        """
        Returns the labels associated with the given board.
        
        :param board: The board to retrieve labels for.
        :type board: Board
        :return: The labels associated with the given board.
        :rtype: QuerySet[Label]
        """
        return Label.objects.filter(board=self)
    

    
    def get_status_choices(self):
        """
        Returns a list of choices for the status field of a Task object.
        
        :return: A list of choices for the status field of a Task object.
        :rtype: list[str]
        """
        return TaskList.objects.filter(board=self).values_list('title', flat=True)

    def archive(self):
        list_qs = self.board_Tasklists.all()
        task_qs = Task.objects.filter(status__in = list_qs)
        task_qs.archive()
        list_qs.archive()
        return super().archive()
    
    def restore(self):
        list_qs = self.board_Tasklists(manager = 'original_objects').all()
        task_qs = Task.original_objects.filter(status__in = list_qs)
        task_qs.restore()
        list_qs.restore()
        return super().restore()


class TaskList(BaseModel, SoftDeleteMixin):
    title = models.CharField(_("Title"), max_length=150, help_text='Title of the Tasklist')
    board = models.ForeignKey(Board, verbose_name=_("Board"), on_delete=models.CASCADE, help_text='Board associated with the Tasklist', related_name='board_Tasklists')

    class Meta:
        verbose_name = _("TaskList")
        verbose_name_plural = _("TaskLists")
        ordering = ["board"]

    def __str__(self):
        return f'{self.title} - related board: {self.board}'

    def add_task(self, title, description='', labels=None, start_date=None, end_date=None, assigned_to=None):
        return Task.create_task(
            title=title,
            status=self,
            description=description,
            start_date=start_date,
            end_date=end_date,
            labels=labels,
            assigned_to=assigned_to,
        )

    def task_count(self):
        return self.status_tasks.all().count()

    def archive(self):
        self.status_tasks.all().archive()
        return super().archive()
    
    def restore(self):
        self.status_tasks(manager = 'original_objects').all().restore()
        return super().restore()
    

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
        """
        Creates a new Label object with the given parameters.
        
        :param title: The title of the label.
        :type title: str
        :param board: The board associated with the label.
        :type board: Board
        :return: The created Label object.
        :rtype: Label
        """
        label = cls.objects.get_or_create(title=title, board=board)
        return label
    

        # Create an Activity object to log the deletion of the label
        # message = f"{user.get_full_name()} deleted the label {self.title} on task {task.title}."
        # Activity.objects.create(task=task, doer=user, message=message)

            
    def get_label_choices():
        """
        Returns a list of choices for the labels field of a Task object.
        
        :return: A list of choices for the labels field of a Task object.
        :rtype: list[str]
        """
        return Label.objects.values_list('title',flat=True)

    
    def get_tasks(self):
        """
        Returns the tasks associated with the Label object.
        
        :return: The tasks associated with the Label object.
        :rtype: QuerySet[Task]
        """
        return self.label_tasks.all()
    
    def get_task_count(self):
        """
        Returns the count of tasks associated with the Label object.
        
        :return: The count of tasks associated with the Label object.
        :rtype: int
        """
        return self.label_tasks.count()


class Task(BaseModel, SoftDeleteMixin):
    title = models.CharField(max_length=300, verbose_name=_('Title'), help_text='Title of the task')
    description = models.TextField(verbose_name=_('Description'), help_text='Description of the task')
    status = models.ForeignKey(TaskList ,verbose_name=_('Status'), on_delete=models.CASCADE, help_text='Status of the task', related_name='status_tasks')
    order = models.IntegerField(verbose_name=_('Order'), help_text='Order of the task',default=1)
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
    def create_task(cls, doer, title, description, status, labels=None, start_date=None, end_date=None, assigned_to=None):
        """
        Creates a new Task object with the given parameters.
        
        :param title: The title of the task.
        :type title: str
        :param description: The description of the task.
        :type description: str
        :param status: The status of the task.
        :type status: TaskList
        :param order: The order of the task.
        :type order: int
        :param labels: The labels associated with the task (optional).
        :type labels: list[Label]
        :param start_date: The start date of the task (optional).
        :type start_date: datetime.datetime
        :param end_date: The end date of the task (optional).
        :type end_date: datetime.datetime
        :param assigned_to: The users assigned to the task (optional).
        :type assigned_to: list[User]
        :return: The created Task object.
        :type: Task
        """

        order = status.task_count() + 1

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
        message = f"A new task {title} was created."
        Activity.objects.create(task=task, doer=doer, message=message)
    
    def update_task(self, doer, title=None, description=None, status=None, order=None, labels=None,start_date=None, end_date=None, assigned_to=None):
        """
        Updates the Task object with the given parameters.
        
        :param title: The new title of the task (optional).
        :type title: str
        :param description: The new description of the task (optional).
        :type description: str
        :param status: The new status of the task (optional).
        :type status: TaskList
        :param order: The new order of the task (optional).
        :type order: int
        :param labels: The new labels associated with the task (optional).
        :type labels: list[Label]
        :param start_date: The new start date of the task (optional).
        :type start_date: datetime.datetime
        :param end_date: The new end date of the task (optional).
        :type end_date: datetime.datetime
        :param assigned_to: The new users assigned to the task (optional).
        :type assigned_to: list[User]
        """
        messages = []
        if title is not None:
            self.title = title
            message = f"Task title was changed to {self.title}."
            messages.append(message)
        if description is not None:
            self.description = description
            message = f"Task description was changed."
            messages.append(message)
        if status is not None:
            self.status = status
            message = f"Task status was changed to {self.status.title}."
            messages.append(message)
        if order is not None:
            self.order = order
        if start_date is not None:
            self.start_date = start_date
            message = f"Task start date was changed to {self.start_date}."
            messages.append(message)
        if end_date is not None:
            self.end_date = end_date
            message = f"Task end date was changed to {self.end_date}."
            messages.append(message)
        if labels is not None:
            self.labels.set(labels, clear=True)
        if assigned_to is not None:
            new_assigned_to = [user for user in assigned_to if user not in list(self.assigned_to.all())]
            deleted_assigned_to = [user for user in list(self.assigned_to.all()) if user not in assigned_to]
            self.assigned_to.set(assigned_to, clear=True)
            for user in new_assigned_to:
                message = f"Task assined to {user.get_full_name()}."
                messages.append(message)
            for user in deleted_assigned_to:
                message = f"{user.get_full_name()} removed from task assigness."
                messages.append(message)

        self.save()

        for message in messages:
            Activity.objects.create(task=self, doer=doer, message=message)
    


    def get_comment(self):
        """
        Returns the comments associated with the Task object.

        :return: The comments associated with the Task object.
        :rtype: QuerySet[Comment]
        """
        return self.task_comments.all()
    
    def get_attachments(self):
        """
        Returns the attachments associated with the Task object.
        
        :return: The attachments associated with the Task object.
        :rtype: QuerySet[Attachment]
        """
        return self.task_attachments.all()
    
    def get_activity(self):
        """
        Returns the activities associated with the Task object.
        
        :return: The activities associated with the Task object.
        :rtype: QuerySet[Activity]
        """
        return self.task_activity.all()
    
    def get_assigned_users(self):
        """
        Returns the users assigned to the Task object.
        
        :return: The users assigned to the Task object.
        :rtype: QuerySet[User]
        """
        return self.assigned_to.all()

    def get_task_comments_count(self):
        """
        Returns the count of comments on the given task.
        
        :param task: The task to count comments for.
        :type task: Task
        :return: The count of comments on the given task.
        :rtype: int
        """

        return self.task_comments.all().count()
    
    def get_task_comments(self):
        """
        Returns the comments on the same task as the Comment object.
        
        :return: The comments on the same task as the Comment object.
        :rtype: QuerySet[Comment]
        """
        return self.task_comments.all()


    
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
    
    def create_comment(cls, body, task, author, parent=None):
        """
        Creates a new Comment object with the given parameters.
        
        :param body: The body of the comment.
        :type body: str
        :param task: The task associated with the comment.
        :type task: Task
        :param author: The author of the comment.
        :type author: User
        :param parent: The parent comment (optional).
        :type parent: Comment
        :return: The created Comment object.
        :rtype: Comment
        """
        comment = cls.objects.create(body=body, task=task, author=author, parent=parent)
    
        # Create an Activity object to log the creation of the comment
        if parent:
            message = f"{author.get_full_name()} replied to a comment on task {task.title}."
        else:
            message = f"{author.get_full_name()} added a new comment on task {task.title}."
    
        Activity.objects.create(task=task, doer=author, message=message)
    
        return comment
   
    def update_comment(self, body=None):
        """
        Updates the Comment object with the given body.
        
        :param body: The new body of the comment (optional).
        :type body: str
        """
        if body is not None:
            self.body = body
            self.save
            message = f"{self.author.get_full_name()} updated a comment on task {self.task.title}."
            Activity.objects.create(task=self.task, doer=self.author, message=message)

    def archive(self):
        """
        Soft-deletes the Comment object.
        """
        # Create an Activity object to log the deletion of the comment
        message = f"{self.author.get_full_name()} deleted a comment on task {self.task.title}."
        Activity.objects.create(task=self.task, doer=self.author, message=message)

        return super().archive()

    
    def get_replies(self):
        """
        Returns the replies to the Comment object.
        
        :return: The replies to the Comment object.
        :rtype: QuerySet[Comment]
        """
        return Comment.objects.filter(parent=self)
    
    def get_author_comments(self):
        """
        Returns the comments by the same author as the Comment object.
        
        :return: The comments by the same author as the Comment object.
        :rtype: QuerySet[Comment]
        """
        return Comment.objects.filter(author=self.author, task__status__board=self.task.status.board)
    

class Attachment(BaseModel , SoftDeleteMixin):
    file = models.FileField(verbose_name=_("file") , max_length=100 ,upload_to='uploads/attachments/' , blank=True)
    task = models.ForeignKey(Task,verbose_name=_('Task'), on_delete=models.CASCADE,  help_text='Task of the attachment', related_name='task_attachments')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Owner"), on_delete=models.DO_NOTHING, related_name='owner_attachments')

    @classmethod
    def create(cls, file, task, owner):
        attachment = cls.objects.create(file=file,task=task, owner=owner)
        message = f"{owner.get_full_name()} attached a new file."
        Activity.objects.create(task= task, doer=owner, message = message)
        return attachment
    
    def archive(self):
        """
        Soft-deletes the Comment object.
        """
        # Create an Activity object to log the deletion of the comment
        message = f"{self.owner.get_full_name()} deleted a attachment on task {self.task.title}."
        Activity.objects.create(task=self.task, doer=self.owner, message=message)

        return super().archive()


    def owner_other_attachments_on_board(self):
        return Attachment.objects.filter(owner= self.owner, task__status__board = self.task.status.board)


    def owner_other_attachments_on_board(self):
        return self.objects.filter(owner= self.owner, task__status__board__in= self.task.status.board)

    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural =_("Attachments")


    def __str__(self):
        return f"Attached by {self.owner.get_full_name()}."


class Activity(BaseModel):

    doer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name=_('Doer'), help_text='Doer of the activity', related_name='doer_activity')
    message = models.TextField(verbose_name=_('message'), max_length=300 , help_text='message of the activity')
    task = models.ForeignKey(Task,verbose_name=_('Task'), on_delete=models.CASCADE,  help_text='Task associated with the activity', related_name='task_activity')
    
    @classmethod
    def attachment_activity_on_board(cls, board: Board):
        return cls.objects.filter(task__status__board= board, message__contains='attached')

    @classmethod
    def task_create_activity_on_board(cls, board: Board):
        return cls.objects.filter(task__status__board= board, message__contains='new task')

    @classmethod
    def from_to_date_on_board(cls, from_date, to_date, board: Board):
        return cls.objects.filter(task__status__board= board, create_at__gt=from_date, create_at__lte=to_date)

    def doer_other_activitys_on_board(self):
        return self.doer.activities_on_board(self.task.status.board)
    
    class Meta:
        verbose_name = _('Activitie')
        verbose_name_plural =_("Activities")
        ordering = ["create_at"]


    def __str__(self):
        return f'{self.create_at} - {self.message}'
