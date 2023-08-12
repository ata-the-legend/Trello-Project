from django.test import TestCase
from .models import Activity , Attachment , Comment , Task , Label , TaskList , Board , WorkSpace
from trello.apps.accounts.models import User
# Create your tests here.

class ActivityTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@example.com", password="password")
        self.workspace = WorkSpace.objects.create(title='Test Workspace')
        self.board = Board.objects.create(title='Test Board')
        self.tasklist = TaskList.objects.create(title='Test Task List')
        self.label = Label.objects.create(title='Test Label')
        self.task = Task.objects.create(title='Test Task', description='Test Description', status=self.task_list, order=1)
        self.task.labels.add(self.label)
        self.task.save()
        self.activity_doer = get_user_model().objects.create_user(username='activitydoer', password='testpassword')
        self.activity = Activity.objects.create(doer=self.activity_doer, message='Test Activity', task=self.task)

    def test_attach_activity_in_board(self):
        Activity.attach_activity_in_board(self.board)


    def test_task_create_activity_in_board(self):
        Activity.task_create_activity_in_board(self.board)


    def test_from_to_date(self):
        from_date = datetime.now() - timedelta(days=7)
        to_date = datetime.now()
        activities = Activity.from_to_date(from_date, to_date)


    def test_doer_other_activitys_on_board(self):
        activities = self.activity.doer_other_activitys_on_board()




class AttachmentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@example.com", password="password")
        self.workspace = WorkSpace.objects.create(title='Test Workspace')
        self.board = Board.objects.create(title='Test Board')
        self.tasklist = TaskList.objects.create(title='Test Task List')
        self.label = Label.objects.create(title='Test Label')
        self.task = Task.objects.create(title='Test Task', description='Test Description', status=self.task_list, order=1)
        self.task.labels.add(self.label)
        self.task.save()
        self.attachment_owner = get_user_model().objects.create_user(username='attachmentowner', password='testpassword')
        self.attachment = Attachment.objects.create(file='testfile.pdf', task=self.task, owner=self.attachment_owner)

    def test_create_attachment(self):
        attachment = Attachment.create(file='testfile.pdf', task=self.task, owner=self.attachment_owner)
        self.assertIsNotNone(attachment)
        activity = Activity.objects.filter(task=self.task, doer=self.attachment_owner, message=f"{self.attachment_owner.get_full_name()} attached a new file.")
        self.assertTrue(activity.exists())

    def test_owner_other_attachments_on_board(self):
        attachments = self.attachment.owner_other_attachments_on_board()
        self.assertIn(self.attachment, attachments)