from django.conf import settings
from django.db import models
from trello.apps.core.models import BaseModel, SoftDeleteMixin
from django.db.models.query import QuerySet
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

class WorkSpace(BaseModel, SoftDeleteMixin):
    title = models.CharField(
        _("Title"), 
        max_length=150, 
        help_text='Title of the workspace'
        )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        verbose_name=_("Members"), 
        help_text='members of the workspace', 
        related_name='member_work_spaces'
        )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name=_("Owner"), 
        on_delete=models.CASCADE, 
        help_text='The owner of the workspace', 
        related_name='owner_work_spaces'
        )

    class Meta:
        verbose_name = _("WorkSpace")
        verbose_name_plural = _("WorkSpaces")
        ordering = ["-create_at"]

    def __str__(self) -> str:
        return f'{self.title} - owned by {self.owner}'

    def add_member(self, member):
        """
        Add new member to the work space.
        """
        self.members.add(
            member
            )
        return self

    def add_board(self, title: str, background_image) -> QuerySet:
        """
        Add new board to the work space.
        """
        if background_image is None:
            Board.objects.create(
                title=title, 
                work_space=self
                )
            return self.work_space_boards.filter(
                title=title
                )
        Board.objects.create(
            title=title, 
            work_space=self, 
            background_image=background_image
            )
        return self.work_space_boards.filter(
            title=title
            )

    def work_space_members(self) -> QuerySet:
        """
        Return list of work space members.
        """
        return self.members.all()
    
    def archive(self) -> None:
        board_qs = self.work_space_boards.all()
        list_qs = TaskList.objects.filter(
            board__in = board_qs
            )
        task_qs = Task.objects.filter(
            status__in = list_qs
            )
        task_qs.archive()
        list_qs.archive()
        board_qs.archive()
        return super().archive()
    
    def restore(self) -> None:
        board_qs = self.work_space_boards(
            manager = 'original_objects'
            ).all()
        list_qs = TaskList.original_objects.filter(
            board__in = board_qs
            )
        task_qs = Task.original_objects.filter(
            status__in = list_qs
            )
        task_qs.restore()
        list_qs.restore()
        board_qs.restore()
        return super().restore()

    def clean(self) -> None:
        """
        check wether the owner is in members list.
        """
        if self.owner in self.members.all():
            raise ValidationError('Owner cant be member')
        return super().clean()


class Board(BaseModel, SoftDeleteMixin):
    title = models.CharField(
        _("Title"), 
        max_length=150, 
        help_text='Title of the board'
        )
    work_space = models.ForeignKey(
        WorkSpace, 
        verbose_name=_("Workspace"), 
        on_delete=models.CASCADE, 
        help_text='work space of the board', 
        related_name='work_space_boards'
        )
    background_image = models.ImageField(
        _("Background image"), 
        upload_to='uploads/backgrounds/', 
        default='uploads/backgrounds/default_background.jpg'
        )

    class Meta:
        verbose_name = _("Board")
        verbose_name_plural = _("Boards")
        ordering = ["work_space"]

    def __str__(self) -> str:
        return f'{self.title} - related work space: {self.work_space}'

    def add_tasklist(self, title: str) -> QuerySet:
        """
        Add new task list to the board.
        """
        return TaskList.objects.create(
            title=title, 
            board=self
            )
    
    def get_board_labels(self) -> QuerySet:
        """
        Returns the labels associated with the board.
        """
        return Label.objects.filter(
            board=self
            )

    def get_status_choices(self) -> QuerySet:
        """
        Returns a list of choices for the status field of a Task object.
        """
        return TaskList.objects.filter(
            board=self
            )

    def archive(self) -> None:
        list_qs = self.board_Tasklists.all()
        task_qs = Task.objects.filter(
            status__in = list_qs
            )
        task_qs.archive()
        list_qs.archive()
        return super().archive()
    
    def restore(self) -> None:
        list_qs = self.board_Tasklists(
            manager = 'original_objects'
            ).all()
        task_qs = Task.original_objects.filter(
            status__in = list_qs
            )
        task_qs.restore()
        list_qs.restore()
        return super().restore()


class TaskList(BaseModel, SoftDeleteMixin):
    title = models.CharField(
        _("Title"), 
        max_length=150, 
        help_text='Title of the Tasklist'
        )
    board = models.ForeignKey(
        Board, verbose_name=_("Board"), 
        on_delete=models.CASCADE, 
        help_text='Board associated with the Tasklist', 
        related_name='board_Tasklists'
        )

    class Meta:
        verbose_name = _("TaskList")
        verbose_name_plural = _("TaskLists")
        ordering = ["board"]

    def __str__(self) -> str:
        return f'{self.title} - related board: {self.board}'

    def add_task(self, doer, title: str, description: str ='',
         start_date=None, end_date=None):
        """
        Add new tak to the task list.
        """
        return Task.create_task(
            doer=doer,
            title=title,
            status=self,
            description=description,
            start_date=start_date,
            end_date=end_date,
        )

    def task_count(self) -> QuerySet:
        """
        Returns the count of tasks that associated with the task list.
        """
        return self.status_tasks.all().count()

    def archive(self) -> None:
        self.status_tasks.all().archive()
        return super().archive()
    
    def restore(self) -> None:
        self.status_tasks(manager = 'original_objects').all().restore()
        return super().restore()
    

class Label(BaseModel):
    title = models.CharField(
        max_length=300, 
        verbose_name=_('Title'), 
        help_text='Title of the label'
        )
    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, 
        verbose_name=_('Board'), 
        help_text='Board associated with the label', 
        related_name='board_labels'
        )
    
    class Meta:
        verbose_name = _('Label')
        verbose_name_plural =_("Labels")
        unique_together = ["title", "board"]

    def __str__(self):
        return self.title
    
    def get_label_choices() -> QuerySet:
        """
        Returns a list of choices for the labels field of the Task object.
        """
        return Label.objects.values_list(
            'title',flat=True
            )

    def get_tasks(self) -> QuerySet:
        """
        Returns the tasks associated with the Label object.
        """
        return self.label_tasks.all()
    
    def get_task_count(self) -> QuerySet:
        """
        Returns the count of tasks associated with the Label object.
        """
        return self.label_tasks.count()


class Task(BaseModel, SoftDeleteMixin):
    title = models.CharField(
        max_length=300, 
        verbose_name=_('Title'), 
        help_text='Title of the task'
        )
    description = models.TextField(
        verbose_name=_('Description'), 
        help_text='Description of the task'
        )
    status = models.ForeignKey(
        TaskList,
        verbose_name=_('Status'), 
        on_delete=models.CASCADE, 
        help_text='Status of the task', 
        related_name='status_tasks'
        )
    order = models.IntegerField(
        verbose_name=_('Order'), 
        help_text='Order of the task',
        default=1)
    labels = models.ManyToManyField(
        Label, verbose_name=_('Label'), 
        help_text='Label associated with the task', 
        related_name='label_tasks'
        )
    start_date = models.DateTimeField(
        verbose_name=_('Start Date'), 
        help_text='Start date of the task', 
        null=True, blank=True
        )
    end_date = models.DateTimeField(
        verbose_name=_('End Date'), 
        help_text='End date of the task', 
        null=True, 
        blank=True
        )
    assigned_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        verbose_name=_('Assigned To'), 
        help_text='User assigned to the task', 
        related_name='assigned_tasks'
        )

    class Meta:
        verbose_name =_('Task')
        verbose_name_plural =_('Tasks')

    def __str__(self) -> str:
        return f'Task {self.title}'
    
    @classmethod
    def create_task(cls, doer, *args, **kwargs):
        """
        Creates a new Task object with the given parameters.
        Doer, title and status fields are required.
        """
        order = kwargs['status'].task_count() + 1
        
        task = cls.objects.create(
            *args,
            **kwargs,
            order=order,
        )
        message = f"Task '{kwargs['title']}' was created."
        Activity.objects.create(
            task=task, 
            doer=doer, 
            message=message
            )
        return task
    
    def update_task(self, doer, *args, **kwargs):
        """
        Updates the Task object with the given parameters.
        """
        messages = []
        if title := kwargs.get('title', None):
            if title != self.title:
                self.title = title
                message = f"Task title was changed to {self.title}."
                messages.append(
                    message
                    )
        if description := kwargs.get('description', None):
            if description != self.description:
                self.description = description
                message = f"Task description was changed."
                messages.append(
                    message
                    )
        if status := kwargs.get('status', None):
            if status != self.status:
                self.status = status
                message = f"Task status was changed to {self.status.title}."
                messages.append(
                    message
                    )
        if order := kwargs.get('order', None):
            if order != self.order:
                self.order = order
        if start_date := kwargs.get('start_date', None):
            if start_date != self.start_date:
                self.start_date = start_date
                message = f"Task start date was changed to {self.start_date}."
                messages.append(
                    message
                    )
        if end_date := kwargs.get('end_date', None):
            if end_date != self.end_date:
                self.end_date = end_date
                message = f"Task end date was changed to {self.end_date}."
                messages.append(
                    message
                    )
        self.save()
        if labels := kwargs.get('labels', None):
            self.labels.set(
                labels, 
                clear=True
                )
        if assigned_to := kwargs.get('assigned_to', None):
            new_assigned_to = [user for user in assigned_to if user not in list(self.assigned_to.all())]
            deleted_assigned_to = [user for user in list(self.assigned_to.all()) if user not in assigned_to]
            self.assigned_to.set(
                assigned_to, 
                clear=True
                )
            for user in new_assigned_to:
                message = f"Task assined to {user}."
                messages.append(
                    message
                    )
            for user in deleted_assigned_to:
                message = f"{user} removed from task assigness."
                messages.append(
                    message
                    )
        for message in messages:
            Activity.objects.create(
                task=self, 
                doer=doer, 
                message=message
                )

    def get_comment(self) -> QuerySet:
        """
        Returns the comments associated with the Task object.
        """
        return self.task_comments.all()
    
    def get_attachments(self):
        """
        Returns the attachments associated with the Task object.
        """
        return self.task_attachments.all()
    
    def get_activity(self) -> QuerySet:
        """
        Returns the activities associated with the Task object.
        """
        return self.task_activity.all()
    
    def get_assigned_users(self) -> QuerySet:
        """
        Returns the users assigned to the Task object.
        """
        return self.assigned_to.all()

    def get_task_comments_count(self) -> QuerySet:
        """
        Returns the count of comments on the given task.
        """
        return self.task_comments.all().count()
    
    def get_task_comments(self) -> QuerySet:
        """
        Returns the comments on the same task as the Comment object.
        """
        return self.task_comments.all()
    

class Comment(BaseModel, SoftDeleteMixin):
    body = models.TextField(
        verbose_name=_('Body'), 
        help_text='Body of the comment'
        )
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        verbose_name=_('Task'), 
        help_text='Task associated with the comment', 
        related_name='task_comments'
        )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.DO_NOTHING, 
        verbose_name=_('Author'), 
        help_text='Author of the comment', 
        related_name='author_comments'
        )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, 
        verbose_name=_('Parent'), 
        null=True, 
        blank=True
        )


    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural =_('Comments')

    def __str__(self) -> str:
        return f'Comment by {self.author} on task {self.task}'
    
    @classmethod
    def create_comment(cls, body: str, task: Task, author, parent=None):
        """
        Creates a new Comment object with the given parameters.
        """
        comment = cls.objects.create(
            body=body, 
            task=task, 
            author=author, 
            parent=parent
            )
        # Create an Activity object to log the creation of the comment
        if parent:
            message = f"{author} replied to a comment on task {task.title}."
        else:
            message = f"{author} added a new comment on task {task.title}."
        Activity.objects.create(task=task, doer=author, message=message)
        return comment
   
    def update_comment(self, body: str | None =None) -> None:
        """
        Updates the Comment object with the given body.
        """
        if body is not None:
            self.body = body
            self.save()
            message = f"{self.author} updated a comment on task {self.task.title}."
            Activity.objects.create(
                task=self.task, 
                doer=self.author, 
                message=message
                )

    def archive(self) -> None:
        """
        Soft-deletes the Comment object.
        """
        # Create an Activity object to log the deletion of the comment
        message = f"{self.author} deleted a comment on task {self.task.title}."
        Activity.objects.create(
            task=self.task, 
            doer=self.author, 
            message=message
            )
        return super().archive()

    def get_replies(self) -> None:
        """
        Returns the replies to the Comment object.
        """
        return Comment.objects.filter(
            parent=self
            )
    
    def get_author_comments(self) -> QuerySet:
        """
        Returns the comments by the same author as the Comment object.
        """
        return Comment.objects.filter(
            author=self.author, 
            task__status__board=self.task.status.board
            )
    

class Attachment(BaseModel , SoftDeleteMixin):
    file = models.FileField(
        verbose_name=_("file"), 
        max_length=100 ,upload_to='uploads/attachments/', 
        blank=True
        )
    task = models.ForeignKey(
        Task,
        verbose_name=_('Task'), 
        on_delete=models.CASCADE,  
        help_text='Task of the attachment', 
        related_name='task_attachments'
        )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name=_("Owner"), 
        on_delete=models.DO_NOTHING, 
        related_name='owner_attachments'
        )

    @classmethod
    def create(cls, file, task: Task, owner):
        attachment = cls.objects.create(
            file=file,
            task=task, 
            owner=owner
            )
        message = f"{owner} attached a new file."
        Activity.objects.create(
            task= task, 
            doer=owner, 
            message = message)
        return attachment
    
    def archive(self) -> None:
        # Create an Activity object to log the deletion of the comment
        message = f"{self.owner} deleted a attachment on task {self.task.title}."
        Activity.objects.create(
            task=self.task, 
            doer=self.owner, 
            message=message
            )
        return super().archive()

    def owner_other_attachments_on_board(self) -> QuerySet:
        """
        Returns other attachments of the owner on the board.
        """
        return Attachment.objects.filter(
            owner= self.owner, 
            task__status__board = self.task.status.board
            )

    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural =_("Attachments")

    def __str__(self) -> str:
        return f"Attached by {self.owner}."


class Activity(BaseModel):

    doer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.DO_NOTHING, 
        verbose_name=_('Doer'), 
        help_text='Doer of the activity', 
        related_name='doer_activity'
        )
    message = models.TextField(
        verbose_name=_('message'), 
        max_length=300 , 
        help_text='message of the activity'
        )
    task = models.ForeignKey(
        Task,verbose_name=_('Task'), 
        on_delete=models.CASCADE,  
        help_text='Task associated with the activity', 
        related_name='task_activity'
        )
    
    @classmethod
    def attachment_activity_on_board(cls, board: Board) -> QuerySet:
        """
        Returns attachment activity of the board.
        """
        return cls.objects.filter(
            task__status__board= board, 
            message__contains='attached'
            )

    @classmethod
    def task_create_activity_on_board(cls, board: Board) -> QuerySet:
        """
        Returns task create activity of the board.
        """
        return cls.objects.filter(
            task__status__board= board, 
            message__contains='new task'
            )

    @classmethod
    def from_to_date_on_board(cls, from_date, to_date, board: Board) -> QuerySet:
        """
        Return the activities of the selected time interval of the board.
        """
        return cls.objects.filter(
            task__status__board= board, 
            create_at__gt=from_date, 
            create_at__lte=to_date
            )

    def doer_other_activitys_on_board(self) -> QuerySet:
        """
        Return other activities of the doer.
        """
        return self.doer.activities_on_board(self.task.status.board)
    
    class Meta:
        verbose_name = _('Activitie')
        verbose_name_plural =_("Activities")
        ordering = ["create_at"]


    def __str__(self) -> str:
        return f'Done By {self.doer}'