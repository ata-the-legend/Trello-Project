from django.test import TestCase
from .models import User
from trello.apps.dashboards.models import *
# Create your tests here.

class UserTestCase(TestCase):
    
    def setUp(self) -> None:
        self.user_ata = User.objects.create_user(email='ata@gmail.COM', password='1234', first_name='ata', last_name='test', avatar=None, mobile='01234567890')
        self.user_super = User.objects.create_superuser(email='super@gmail.COM', password='1234', first_name='super', last_name='test', avatar=None, mobile='01234567892')
        self.user_ali = User.objects.create_user(email='ali@gmail.COM', password='1234', first_name='ali', last_name='test', mobile='01234567893')
        self.workspace_ata = WorkSpace.objects.create(title='Ata Workspace', owner=self.user_ata)
        self.workspace_ata.members.add(self.user_ali)
        self.workspace_ata_2 = WorkSpace.objects.create(title='New Workspace', owner=self.user_ata)
        return super().setUp()

    def test_create_superuser(self):
        self.assertTrue(User.objects.filter(is_superuser=True,is_staff=True).exists())
    
    def test_str(self):
        self.assertEqual(str(self.user_ata), f'{self.user_ata.first_name} {self.user_ata.last_name}')

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

