from django.test import TestCase
from trello.apps.dashboards.models import Label, Board, Task, Activity,TaskList,Comment
from trello.apps.accounts.models import User

class LabelTestCase(TestCase):
    def setUp(self):
        self.board = Board.objects.create(title="Test Board")
        self.task = Task.objects.create(title="Test Task", status=self.board)
        self.user = User.objects.create(email="test@example.com", password="password")

    def test_create_label(self):
        label = Label.create_label("Test Label", self.board, self.task, self.user)
        self.assertEqual(label.title, "Test Label")
        self.assertEqual(label.board, self.board)
        activity = Activity.objects.last()
        self.assertEqual(activity.message, f"{self.user.get_full_name()} created a new label Test Label on task {self.task.title}.")

    def test_delete_label(self):
        label = Label.create_label("Test Label", self.board, self.task, self.user)
        label.delete(self.task, self.user)
        activity = Activity.objects.last()
        self.assertEqual(activity.message, f"{self.user.get_full_name()} deleted the label Test Label on task {self.task.title}.")

    def test_update_label(self):
        label = Label.create_label("Test Label", self.board, self.task, self.user)
        label.update_label("Updated Label", self.task, self.user)
        activity = Activity.objects.last()
        self.assertEqual(activity.message, f"{self.user.get_full_name()} updated the label Updated Label on task {self.task.title}.")

class TaskTestCase(TestCase):
    def setUp(self):
        self.tasklist = TaskList.objects.create(title="Test TaskList")
        self.user = User.objects.create(email="test@example.com", password="password")
        self.label = Label.objects.create(title="Test Label", board=self.tasklist.board)

    def test_create_task(self):
        task = Task.create_task("Test Task", "Test Description", self.tasklist, 1, [self.label], assigned_to=[self.user])
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertEqual(task.status, self.tasklist)
        self.assertEqual(task.order, 1)
        self.assertListEqual(list(task.labels.all()), [self.label])
        self.assertListEqual(list(task.assigned_to.all()), [self.user])
        activity = Activity.objects.last()
        self.assertEqual(activity.message, f"A new task Test Task was created.")

    def test_update_task(self):
        task = Task.create_task("Test Task", "Test Description", self.tasklist, 1, [self.label], assigned_to=[self.user])
        task.update_task("Updated Task", "Updated Description", order=2)
        activity = Activity.objects.last()
        self.assertEqual(activity.message, f"Task Updated Task was updated.")

    def test_delete_task(self):
        task = Task.create_task("Test Task", "Test Description", self.tasklist, 1, [self.label], assigned_to=[self.user])
        task.delete()
        activity = Activity.objects.last()
        self.assertEqual(activity.message, f"Task Test Task was deleted.")

class CommentTestCase(TestCase):
    def setUp(self):
        self.task = Task.objects.create(title="Test Task")
        self.user = User.objects.create(email="test@example.com", password="password")

    def test_create_comment(self):
        comment = Comment.create_comment("Test Comment", self.task, self.user)
        self.assertEqual(comment.body, "Test Comment")
        self.assertEqual(comment.task, self.task)
        self.assertEqual(comment.author, self.user)
        activity = Activity.objects.last()
        self.assertEqual(activity.message, f"{self.user.get_full_name()} added a new comment to task {self.task.title}.")

    def test_update_comment(self):
        comment = Comment.create_comment("Test Comment", self.task, self.user)
        comment.update_comment("Updated Comment")
        activity = Activity.objects.last()
        self.assertEqual(activity.message, f"{self.user.get_full_name()} updated a comment on task {self.task.title}.")

    def test_delete_comment(self):
        comment = Comment.create_comment("Test Comment", self.task, self.user)
        comment.delete()
        activity = Activity.objects.last()
        self.assertEqual(activity.message, f"{self.user.get_full_name()} deleted a comment on task {self.task.title}.")