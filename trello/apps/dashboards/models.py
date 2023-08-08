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

    def add_member(self, user, member):
        if self.owner == user:
            self.member = member
            self.save()

    def add_board(self, user, title):
        if self.owner == user:
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

    def add_task(self, user, title):
        if self.owner == user:
            pass

    def add_tasklist(self, user, title):
        if self.owner == user:
            pass


class TaskList(BaseModel, SoftDeleteMixin):
    title = models.CharField(_("Title"), max_length=150, help_text='Title of the Tasklist')
    board = models.ForeignKey(Board, verbose_name=_("Board"), on_delete=models.CASCADE, help_text='Board associated with the Tasklist', related_name='board_Tasklists')

    class Meta:
        verbose_name = _("TaskList")
        verbose_name_plural = _("TaskLists")
        ordering = ["board"]

    def __str__(self):
        return f'{self.title} - related board: {self.board}'

    def add_task(self, user):
        if self.owner == user:
            pass

    def change_tasklist(self, user):
        pass

class Label(BaseModel):
    title = models.CharField(max_length=300, verbose_name=_('Title'), help_text='Title of the label')
    board = models.ForeignKey(Board, on_delete=models.CASCADE, verbose_name=_('Board'), help_text='Board associated with the label', related_name='board_labels')
    
    class Meta:
        verbose_name = _('Label')
        verbose_name_plural =_("Labels")

    def __str__(self):
        return self.title
    
    def create_label(cls, title, board,task,user):
        """
        Creates a new Label object with the given parameters.
        
        :param title: The title of the label.
        :type title: str
        :param board: The board associated with the label.
        :type board: Board
        :return: The created Label object.
        :rtype: Label
        """
        label = cls.objects.create(title=title, board=board)
        message = f"{user.get_full_name()} created a new label {title} on task {task.title}."
        Activity.objects.create(task=task, doer=user, message=message)
        return label
    
    def delete(self, task=None, user=None):
        """
        Soft-deletes the Label object.
        
        :param task: The task associated with the label deletion (optional).
        :type task: Task
        :param user: The user who deleted the label (optional).
        :type user: User
        """
        self.is_deleted = True
        self.save()
    
        # Create an Activity object to log the deletion of the label
        message = f"{user.get_full_name()} deleted the label {self.title} on task {task.title}."
        Activity.objects.create(task=task, doer=user, message=message)

    def update_label(self, title=None, task =None, user = None):
        """
        Updates the Label object with the given title.
        
        :param title: The new title of the label (optional).
        :type title: str
        """
        if title is not None:
            self.title = title
            self.save()
            message = f"{user.get_full_name()} updated the label {self.title} on task {task.title}."
            Activity.objects.create(task=task, doer=user, message=message)
            
    def get_label_choices():
        """
        Returns a list of choices for the labels field of a Task object.
        
        :return: A list of choices for the labels field of a Task object.
        :rtype: list[str]
        """
        return Label.objects.values_list('title',flat=True)

    
    def get_board_labels(board):
        """
        Returns the labels associated with the given board.
        
        :param board: The board to retrieve labels for.
        :type board: Board
        :return: The labels associated with the given board.
        :rtype: QuerySet[Label]
        """
        return Label.objects.filter(board=board)
    



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
    
    
    def create_task(cls, title, description, status, order, labels=None, start_date=None, end_date=None, assigned_to=None):
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
        :rtype: Task
        """
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
        Activity.objects.create(task=task, doer=assigned_to[0], message=message)
        return task
    
    def update_task(self, title=None, description=None, status=None, order=None, labels=None,start_date=None, end_date=None, assigned_to=None):
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

        message = f"Task {self.title} was updated."
        Activity.objects.create(task=self, doer=assigned_to[0], message=message)
    
    def delete(self):
        """
        Soft-deletes the Task object.
        """
        self.is_deleted = True
        self.save()
    
        # Create an Activity object to log the deletion of the task
        message = f"Task {self.title} was deleted."
        Activity.objects.create(task=self, doer=self.assigned_to.first(), message=message)


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
    
    
    def get_status_choices():
        """
        Returns a list of choices for the status field of a Task object.
        
        :return: A list of choices for the status field of a Task object.
        :rtype: list[str]
        """
        return TaskList.objects.values_list('title', flat=True)
    
    
    def get_label_choices():
        """
        Returns a list of choices for the labels field of a Task object.
        
        :return: A list of choices for the labels field of a Task object.
        :rtype: list[str]
        """
        return Label.objects.values_list('title',flat=True)
    
    
    def get_start_date_choices():
        """
        Returns a list of choices for the start_date field of a Task object.
        
        :return: A list of choices for the start_date field of a Task object.
        :rtype: list[datetime.datetime]
        """
        return Task.objects.exclude(start_date=None).values_list('start_date',flat=True).distinct()
    
    def get_end_date_choices():
        """
        Returns a list of choices for the end_date field of a Task object.
        
        :return: A list of choices for the end_date field of a Task object.
        :rtype: list[datetime.datetime]
        """
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
            message = f"{author.get_full_name()} added a new comment to task {task.title}."
    
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

    def delete(self):
        """
        Soft-deletes the Comment object.
        """
        self.is_deleted = True
        self.save()
    
        # Create an Activity object to log the deletion of the comment
        message = f"{self.author.get_full_name()} deleted a comment on task {self.task.title}."
        Activity.objects.create(task=self.task, doer=self.author, message=message)

    
    def get_task_comment_count(task):
        """
        Returns the count of comments on the given task.
        
        :param task: The task to count comments for.
        :type task: Task
        :return: The count of comments on the given task.
        :rtype: int
        """

        return Comment.objects.filter(task=task).count()



    def get_replies(self):
        """
        Returns the replies to the Comment object.
        
        :return: The replies to the Comment object.
        :rtype: QuerySet[Comment]
        """
        return Comment.objects.filter(parent=self)
    
    def get_task_comments(self):
        """
        Returns the comments on the same task as the Comment object.
        
        :return: The comments on the same task as the Comment object.
        :rtype: QuerySet[Comment]
        """
        return Comment.objects.filter(task=self.task)
    
    def get_author_comments(self):
        """
        Returns the comments by the same author as the Comment object.
        
        :return: The comments by the same author as the Comment object.
        :rtype: QuerySet[Comment]
        """
        return Comment.objects.filter(author=self.author)
    

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


    def owner_other_attachments_on_board(self):
        pass

    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural =_("Attachments")


    def __str__(self):
        return f"Attached by {self.owner.name}."


class Activity(BaseModel):

    doer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name=_('Doer'), help_text='Doer of the activity', related_name='doer_activity')
    message = models.TextField(verbose_name=_('message'), max_length=300 , help_text='message of the activity')
    task = models.ForeignKey(Task,verbose_name=_('Task'), on_delete=models.CASCADE,  help_text='Task associated with the activity', related_name='task_activity')
    
    @classmethod
    def attach_activity_in_board(self, board):
        pass

    @classmethod
    def task_create_activity_in_board(self, board):
        pass

    @classmethod
    def from_to_date(self, from_date, to_date):
        pass

    def doer_other_activitys_on_board(self):
        return self.doer.activities_on_board(self.task.status.board)
    
    class Meta:
        verbose_name = _('Activitie')
        verbose_name_plural =_("Activities")
        ordering = ["create_at"]


    def __str__(self):
        return f'{self.update_at} - {self.message}'
