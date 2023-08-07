from django.test import TestCase
from .models import User
from trello.apps.dashboards.models import *
from django.core import mail
# Create your tests here.

class UserTestCase(TestCase):
    
    def setUp(self) -> None:
        self.user_ata = User.objects.create_user(email='ata@gmail.COM', password='1234', first_name='ata', last_name='test', avatar=None, mobile='01234567890')
        self.user_super = User.objects.create_superuser(email='super@gmail.COM', password='1234', first_name='super', last_name='test', avatar=None, mobile='01234567892')
        self.user_ali = User.objects.create_user(email='ali@gmail.COM', password='1234', first_name='ali', last_name='test', mobile='01234567893')
        self.workspace_ata = WorkSpace.objects.create(title='Ata Workspace', owner=self.user_ata)
        self.workspace_ata.members.add(self.user_ali)
        self.workspace_ata_2 = WorkSpace.objects.create(title='New Workspace', owner=self.user_ata)
        self.board_ata_1_1 = Board.objects.create(title='Board One', work_space=self.workspace_ata)
        self.board_ata_1_2 = Board.objects.create(title='Board Two', work_space=self.workspace_ata)
        self.board_ata_2_1 = Board.objects.create(title='Board Three', work_space=self.workspace_ata_2)
        self.list_1_1_1 = TaskList.objects.create(title='List One', board= self.board_ata_1_1)
        self.list_1_1_2 = TaskList.objects.create(title='List Two', board= self.board_ata_1_1)
        self.list_1_2_1 = TaskList.objects.create(title='List Three', board= self.board_ata_1_2)
        self.list_2_1_1 = TaskList.objects.create(title='List Four', board= self.board_ata_2_1)
        self.task_1 = Task.objects.create(title='Task One', description='...', status=self.list_1_1_1, order=1)
        self.task_2 = Task.objects.create(title='Task Two', description='...', status=self.list_1_1_1, order=2)
        self.task_3 = Task.objects.create(title='Task Three', description='...', status=self.list_1_1_2, order=1)
        self.task_4 = Task.objects.create(title='Task Four', description='...', status=self.list_1_2_1, order=1)
        self.task_5 = Task.objects.create(title='Task Five', description='...', status=self.list_2_1_1, order=1)
        self.task_1.assigned_to.add(self.user_ata)
        self.task_1.assigned_to.add(self.user_ali)
        self.task_2.assigned_to.add(self.user_ata)
        self.task_3.assigned_to.add(self.user_ali)
        self.task_4.assigned_to.add(self.user_ali)
        self.activity_1_1 = Activity.objects.create(doer= self.user_ata,task=self.task_1, message= 'Message One')
        self.activity_1_2 = Activity.objects.create(doer= self.user_ali,task=self.task_1, message= 'Message Two')
        self.activity_2_1 = Activity.objects.create(doer= self.user_ata,task=self.task_2, message= 'Message Three')
        self.activity_3_1 = Activity.objects.create(doer= self.user_ali,task=self.task_3, message= 'Message Four')
        self.activity_3_2 = Activity.objects.create(doer= self.user_ali,task=self.task_3, message= 'Message Five')
        self.activity_3_3 = Activity.objects.create(doer= self.user_ali,task=self.task_3, message= 'Message Six')
        self.activity_4_1 = Activity.objects.create(doer= self.user_ata,task=self.task_4, message= 'Message Seven')
        
        return super().setUp()

    def test_create_superuser(self):
        self.assertTrue(User.objects.filter(is_superuser=True,is_staff=True).exists())
    
    def test_str(self):
        self.assertEqual(str(self.user_ata), f'{self.user_ata.first_name} {self.user_ata.last_name}')

    def test_fields(self):
        self.assertEqual(self.user_ata.avatar, "uploads/avatars/default.jpg")
        self.assertEqual(self.user_ata.first_name, "ata")
        self.assertEqual(self.user_ata.last_name, "test")
        self.assertEqual(self.user_ata.mobile, "01234567890")
        self.assertTrue(self.user_ata.check_password('1234'))        

    def test_clean(self):
        # print(self.user_ata.email)
        user = User.objects.create(email='test@gmail.COM', password='1234', first_name='test', last_name='test', avatar=None, mobile='01234567891')
        self.assertEqual(user.email, 'test@gmail.COM')
        user.clean()
        self.assertEqual(user.email, 'test@gmail.com')

    def test_get_short_name(self):
        self.assertEqual(self.user_ata.get_short_name(), 'ata')

    def test_archive(self):
        self.assertTrue(self.user_ata.is_active)
        self.user_ata.archive()
        self.assertFalse(self.user_ata.is_active)
    
    def test_restore(self):
        self.user_ata.archive()
        self.assertFalse(self.user_ata.is_active)
        self.user_ata.restore()
        self.assertTrue(self.user_ata.is_active)

    def test_membered_workspaces(self):
        self.assertCountEqual(self.user_ali.membered_workspaces(),[self.workspace_ata])
        self.assertCountEqual(self.user_ata.membered_workspaces(),[])

    def test_owened_workspases(self):
        self.assertCountEqual(self.user_ata.owened_workspases(),[self.workspace_ata, self.workspace_ata_2])
        self.assertCountEqual(self.user_ali.owened_workspases(),[])


    def test_tasked_boards(self):
        self.assertCountEqual(self.user_ali.tasked_boards(), [self.board_ata_1_1, self.board_ata_1_2])
        self.assertCountEqual(self.user_ata.tasked_boards(), [self.board_ata_1_1])

    def test_active_tasks(self):
        self.task_4.is_active = False
        self.task_4.save()
        # print(self.user_ali.active_tasks())
        self.assertCountEqual(self.user_ali.active_tasks(), [self.task_1, self.task_3])
        self.assertCountEqual(self.user_ata.active_tasks(), [self.task_1, self.task_2])

    def test_activities_on_board(self):
        self.assertCountEqual(self.user_ali.activities_on_board(self.board_ata_1_1), [self.activity_1_2, self.activity_3_1, self.activity_3_2, self.activity_3_3])
        self.assertCountEqual(self.user_ali.activities_on_board(self.board_ata_1_2), [])
        self.assertCountEqual(self.user_ata.activities_on_board(self.board_ata_1_1), [self.activity_1_1, self.activity_2_1])
        self.assertCountEqual(self.user_ata.activities_on_board(self.board_ata_1_2), [self.activity_4_1])
        self.assertCountEqual(self.user_ata.activities_on_board(self.board_ata_2_1), [])

    def test_teammates_in_workspace(self):
        self.assertCountEqual(self.user_ata.teammates_in_workspace(self.workspace_ata), [self.user_ali])
        self.assertCountEqual(self.user_ata.teammates_in_workspace(self.workspace_ata_2), [])
        self.assertCountEqual(self.user_ali.teammates_in_workspace(self.workspace_ata), [self.user_ata])
    
    def test_required_email(self):
        with self.assertRaises(ValueError):
            user = User.objects.create_user(email='', password='1234', first_name='test', last_name='test', avatar=None, mobile='01234567891')

    def test_superuser_default_fields(self):
        with self.assertRaises(ValueError):
            user = User.objects.create_superuser(email='newsuper@gmail.com', is_staff=False, password='1234', first_name='test', last_name='test', avatar=None, mobile='01234567891')
        with self.assertRaises(ValueError):
            user = User.objects.create_superuser(email='newsuper@gmail.com', is_superuser=False, password='1234', first_name='test', last_name='test', avatar=None, mobile='01234567891')
        
    def test_send_email(self):
        # Send message.
        self.user_ata.email_user(
            "Subject",
            "Test message.",
        )
        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, "Subject")
