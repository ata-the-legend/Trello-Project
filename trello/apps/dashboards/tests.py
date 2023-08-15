from django.test import TestCase
from trello.apps.dashboards.models import *
from trello.apps.accounts.models import User
from django.utils import timezone

# class LabelTestCase(TestCase):
#     def setUp(self):
#         self.board = Board.objects.create(title="Test Board")
#         self.task = Task.objects.create(title="Test Task", status=self.board)
#         self.user = User.objects.create(email="test@example.com", password="password")

#     def test_create_label(self):
#         label = Label.create_label("Test Label", self.board, self.task, self.user)
#         self.assertEqual(label.title, "Test Label")
#         self.assertEqual(label.board, self.board)
#         activity = Activity.objects.last()
#         self.assertEqual(activity.message, f"{self.user.get_full_name()} created a new label Test Label on task {self.task.title}.")

#     def test_delete_label(self):
#         label = Label.create_label("Test Label", self.board, self.task, self.user)
#         label.delete(self.task, self.user)
#         activity = Activity.objects.last()
#         self.assertEqual(activity.message, f"{self.user.get_full_name()} deleted the label Test Label on task {self.task.title}.")

#     def test_update_label(self):
#         label = Label.create_label("Test Label", self.board, self.task, self.user)
#         label.update_label("Updated Label", self.task, self.user)
#         activity = Activity.objects.last()
#         self.assertEqual(activity.message, f"{self.user.get_full_name()} updated the label Updated Label on task {self.task.title}.")

# class TaskTestCase(TestCase):
#     def setUp(self):
#         self.tasklist = TaskList.objects.create(title="Test TaskList")
#         self.user = User.objects.create(email="test@example.com", password="password")
#         self.label = Label.objects.create(title="Test Label", board=self.tasklist.board)

#     def test_create_task(self):
#         task = Task.create_task("Test Task", "Test Description", self.tasklist, 1, [self.label], assigned_to=[self.user])
#         self.assertEqual(task.title, "Test Task")
#         self.assertEqual(task.description, "Test Description")
#         self.assertEqual(task.status, self.tasklist)
#         self.assertEqual(task.order, 1)
#         self.assertListEqual(list(task.labels.all()), [self.label])
#         self.assertListEqual(list(task.assigned_to.all()), [self.user])
#         activity = Activity.objects.last()
#         self.assertEqual(activity.message, f"A new task Test Task was created.")

#     def test_update_task(self):
#         task = Task.create_task("Test Task", "Test Description", self.tasklist, 1, [self.label], assigned_to=[self.user])
#         task.update_task("Updated Task", "Updated Description", order=2)
#         activity = Activity.objects.last()
#         self.assertEqual(activity.message, f"Task Updated Task was updated.")

#     def test_delete_task(self):
#         task = Task.create_task("Test Task", "Test Description", self.tasklist, 1, [self.label], assigned_to=[self.user])
#         task.delete()
#         activity = Activity.objects.last()
#         self.assertEqual(activity.message, f"Task Test Task was deleted.")

# class CommentTestCase(TestCase):
#     def setUp(self):
#         self.task = Task.objects.create(title="Test Task")
#         self.user = User.objects.create(email="test@example.com", password="password")

#     def test_create_comment(self):
#         comment = Comment.create_comment("Test Comment", self.task, self.user)
#         self.assertEqual(comment.body, "Test Comment")
#         self.assertEqual(comment.task, self.task)
#         self.assertEqual(comment.author, self.user)
#         activity = Activity.objects.last()
#         self.assertEqual(activity.message, f"{self.user.get_full_name()} added a new comment to task {self.task.title}.")

#     def test_update_comment(self):
#         comment = Comment.create_comment("Test Comment", self.task, self.user)
#         comment.update_comment("Updated Comment")
#         activity = Activity.objects.last()
#         self.assertEqual(activity.message, f"{self.user.get_full_name()} updated a comment on task {self.task.title}.")

#     def test_delete_comment(self):
#         comment = Comment.create_comment("Test Comment", self.task, self.user)
#         comment.delete()
#         activity = Activity.objects.last()
#         self.assertEqual(activity.message, f"{self.user.get_full_name()} deleted a comment on task {self.task.title}.")

class ActivityTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@example.com", password="password")
        self.workspace = WorkSpace.objects.create(title='Test Workspace' , owner=self.user)
        self.board = Board.objects.create(title='Test Board' , work_space=self.workspace)
        self.tasklist = TaskList.objects.create(title='Test Task List' , board=self.board)
        self.label = Label.objects.create(title='Test Label' , board=self.board)
        self.task = Task.create_task(doer=self.user, title='Test Task', description='Test Description', status=self.tasklist)
        self.task.labels.add(self.label)
        self.task.save()
        self.activity = Activity.objects.create(doer= self.user, message ='test', task= self.task)

    def test_attachment_activity_on_board(self):
        activities = Activity.attachment_activity_on_board(self.board)
        self.assertFalse(activities.exists())
        Attachment.create(file='testfile.pdf', task=self.task, owner=self.user)
        activities = Activity.attachment_activity_on_board(self.board)
        self.assertTrue(activities.exists())


    def test_task_create_activity_on_board(self):
        self.assertEqual(Activity.task_create_activity_on_board(self.board).count(), 1)


    def test_from_to_date_on_board(self):
        from_date = timezone.datetime(year=int(self.user.date_joined.year),
                                       month=int(self.user.date_joined.month),
                                        day=int(self.user.date_joined.day),
                                        hour=int(self.user.date_joined.hour),
                                        minute=int(self.user.date_joined.minute),
                                        second=int(self.user.date_joined.second)) - timezone.timedelta(minutes=10)
        to_date = timezone.now()
        activities = Activity.from_to_date_on_board(from_date, to_date, self.board)
        self.assertEqual(activities.count(), 2)


    def test_doer_other_activitys_on_board(self):
        act1 = Attachment.create(file='testfile.pdf', task=self.task, owner=self.user)
        act2 = Attachment.create(file='testfile.pdf', task=self.task, owner=self.user)
        activities = self.activity.doer_other_activitys_on_board()
        self.assertEqual(activities.count(), 4)

    def test_str(self):
        self.assertEqual(str(self.activity), f"{self.activity.create_at} - {self.activity.message}")




class AttachmentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@example.com", password="password")
        self.workspace = WorkSpace.objects.create(title='Test Workspace' , owner=self.user)
        self.board = Board.objects.create(title='Test Board' , work_space=self.workspace)
        self.tasklist = TaskList.objects.create(title='Test Task List' , board=self.board)
        self.label = Label.objects.create(title='Test Label' , board=self.board)
        self.task = Task.objects.create(title='Test Task', description='Test Description', status=self.tasklist, order=1)
        self.task.labels.add(self.label)
        self.task.save()
        self.attachment = Attachment.objects.create(file='testfile.pdf', task=self.task, owner=self.user)

    def test_create(self):
        attachment = Attachment.create(file='testfile.pdf', task=self.task, owner=self.user)
        self.assertIsNotNone(attachment)
        activity = Activity.objects.filter(task=self.task, doer=self.user, message=f"{self.user.get_full_name()} attached a new file.")
        self.assertTrue(activity.exists())

    def test_owner_other_attachments_on_board(self):
        attachments = self.attachment.owner_other_attachments_on_board()
        self.assertIn(self.attachment, attachments)

    def test_archive(self):
        activity = Activity.objects.filter(task=self.task, doer=self.user)
        self.assertFalse(activity.exists())
        self.attachment.archive()
        activity = Activity.objects.filter(task=self.task, doer=self.user)
        self.assertTrue(activity.exists())

    def test_str(self):
        self.assertEqual(str(self.attachment), "Attached by .") 
