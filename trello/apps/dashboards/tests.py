from django.utils import timezone
from django.test import TestCase 
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from trello.apps.dashboards.models import Label, Board ,WorkSpace,Task,TaskList ,Comment , Activity,Attachment
from django.core.exceptions import ValidationError

User = get_user_model()

class LabelTestCase(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(password="testpassword", email="testuser@example.com")
        self.test_workspace = WorkSpace.objects.create(title="Test Workspace", owner=self.test_user)
        self.test_board = Board.objects.create(title="Test Board", work_space=self.test_workspace)
        self.label = Label.objects.create(title="Test Label", board=self.test_board)
        

    def test_get_label_choices(self):
        label_titles = ['Label 1', 'Label 2', 'Label 3']
        for title in label_titles:
            Label.objects.create(title=title, board=self.test_board)
        label_choices = Label.get_label_choices()
        for title in label_titles:
            self.assertIn(title, label_choices)
        self.assertEqual(len(label_titles), len(label_choices) - 1) # - self.label

    
    def test_get_tasks(self):
        self.assertCountEqual(self.label.get_tasks(), self.label.label_tasks.all())
         

    def test_get_task_count(self):
        task_titles = ["Task 1", "Task 2", "Task 3"]
        for title in task_titles:
            task_list = TaskList.objects.create(title="Test TaskList", board=self.test_board)
            task = Task.objects.create(title=title, description="Test description", status=task_list)
            task.labels.add(self.label)
        task_count = self.label.get_task_count()
        self.assertEqual(task_count, len(task_titles))

    
    def test_str(self):
        self.assertEqual(str(self.label), self.label.title)


class CommentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="testuser@example.com", password='testpassword')
        self.work_space = WorkSpace.objects.create(title='Test Workspace', owner=self.user)
        self.board = Board.objects.create(title='Test Board', work_space=self.work_space)
        self.task_list = TaskList.objects.create(title='Test Task List', board=self.board)
        self.task = Task.objects.create(title='Test Task', status=self.task_list)
        self.comment = Comment.objects.create(body='Test Comment', task=self.task, author=self.user)


    def test_create_comment(self):
        parent_comment = Comment.objects.create(body='Parent Comment', task=self.task, author=self.user)

        created_comment = Comment.create_comment(body='New Test Comment', task=self.task, author=self.user, parent=parent_comment)

        self.assertEqual(created_comment.body, 'New Test Comment')
        self.assertEqual(created_comment.task, self.task)
        self.assertEqual(created_comment.author, self.user)
        self.assertEqual(created_comment.parent, parent_comment)
        activity = Activity.objects.last()
        self.assertEqual(activity.task, self.task)
        self.assertEqual(activity.doer, self.user)
        self.assertEqual(activity.message, f"{self.user.email} replied to a comment on task {self.task.title}.")
        created_comment_without_parent = Comment.create_comment(body='Another Test Comment', task=self.task, author=self.user)
        self.assertEqual(created_comment_without_parent.body, 'Another Test Comment')
        self.assertEqual(created_comment_without_parent.task, self.task)
        self.assertEqual(created_comment_without_parent.author, self.user)
        self.assertIsNone(created_comment_without_parent.parent)
        activity_without_parent = Activity.objects.last()
        self.assertEqual(activity_without_parent.task, self.task)
        self.assertEqual(activity_without_parent.doer, self.user)
        self.assertEqual(activity_without_parent.message, f"{self.user.email} added a new comment on task {self.task.title}.")



    def test_str(self):
        self.assertEqual(str(self.comment), f'Comment by {self.user} on task {self.task}')


    def test_archive(self):
        self.comment.archive()
        self.assertFalse(self.comment.is_active)
        self.assertEqual(self.comment.task.task_activity.count(), 1)
        activity = self.comment.task.task_activity.first()
        self.assertEqual(activity.doer, self.user)
        self.assertIn("deleted a comment", activity.message)


    def test_get_replies(self):
        reply1 = Comment.objects.create(body='Test Reply 1', task=self.task, author=self.user, parent=self.comment)
        reply2 = Comment.objects.create(body='Test Reply 2', task=self.task, author=self.user, parent=self.comment)
        replies = self.comment.get_replies()
        self.assertCountEqual(replies, [reply1, reply2])


    def test_get_author_comments(self):
        comment1 = Comment.objects.create(body='Test Comment 1', task=self.task, author=self.user)
        comment2 = Comment.objects.create(body='Test Comment 2', task=self.task, author=self.user)
        author_comments = self.comment.get_author_comments()
        self.assertCountEqual(author_comments, [self.comment, comment1, comment2])


    def test_update_comment(self):
        initial_body = "Initial comment body."
        comment = Comment.objects.create(
            body=initial_body,
            task=self.task,
            author=self.user,
            parent=None
        )

        new_body = "Updated comment body."

        comment.update_comment(body=new_body)
        comment.refresh_from_db()
        self.assertEqual(comment.body, new_body)
        activity_logs = comment.task.task_activity.all()
        self.assertEqual(activity_logs.count(), 1)
        update_activity = activity_logs.latest('create_at')
        self.assertEqual(update_activity.doer, self.user)
        self.assertIn("updated a comment", update_activity.message)


class TaskTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(email="user1@example.com")
        self.user2 = User.objects.create(email="user2@example.com")
        self.owner = User.objects.create(email="owner@example.com")
        self.work_space = WorkSpace.objects.create(title="Test WorkSpace", owner=self.owner)
        self.board = Board.objects.create(title="Test Board", work_space=self.work_space)
        self.task_list = TaskList.objects.create(title="Test Task List", board=self.board)
        self.task_list_2 = TaskList.objects.create(title="Test Task List 2", board=self.board)
        self.label1 = Label.objects.create(title="Label 1", board=self.board)
        self.label2 = Label.objects.create(title="Label 2", board=self.board)
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            status=self.task_list,
        )
        
        self.comment1 = Comment.objects.create(body="Comment 1", task=self.task, author=self.user1)
        self.comment2 = Comment.objects.create(body="Comment 2", task=self.task, author=self.user2)



    def test_create_task(self):
        task = Task.create_task(
            title="Test Task",
            doer=self.owner,
            description="Test Description",
            status=self.task_list,
            start_date=timezone.make_aware(timezone.datetime.strptime("2023-01-01", "%Y-%m-%d")),  # Convert to datetime
            end_date=timezone.make_aware(timezone.datetime.strptime("2023-12-31", "%Y-%m-%d")),    # Convert to datetime
        )
        self.assertEqual(task.start_date.strftime('%Y-%m-%d'), "2023-01-01")
        self.assertEqual(task.end_date.strftime('%Y-%m-%d'), "2023-12-31")
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertEqual(task.status, self.task_list)



    def test_update_task(self):
        new_title = "Updated Title"
        new_description = "Updated Description"
        new_status = self.task_list_2  # Update with a valid TaskList instance
        new_order = 2
        new_labels = [self.label1, self.label2]  # Update with valid Label instances
        new_start_date = timezone.datetime(2023, 8, 1, tzinfo=timezone.utc)
        new_end_date = timezone.datetime(2023, 8, 15, tzinfo=timezone.utc)

        initial_assigned_users = [self.user1, self.user2]
        removed_user = self.user1

        updated_assigned_users = [user for user in initial_assigned_users if user != removed_user]

        self.task.update_task(
            doer=self.user1,
            assigned_to=initial_assigned_users,
        )

        # Call the update_task method
        self.task.update_task(
        doer=self.user1,
        title=new_title,
        description=new_description,
        status=new_status,
        order=new_order,
        labels=new_labels,
        start_date=new_start_date,
        end_date=new_end_date,
        assigned_to=updated_assigned_users,
    )
        # Refresh the object from the database to get the updated values
        self.task.refresh_from_db()

        # Assert the changes
        self.assertEqual(self.task.title, new_title)
        self.assertEqual(self.task.description, new_description)
        self.assertEqual(self.task.status, new_status)
        self.assertEqual(self.task.order, new_order)
        self.assertCountEqual(list(self.task.labels.all()), new_labels)
        self.assertEqual(self.task.start_date, new_start_date)
        self.assertEqual(self.task.end_date, new_end_date)
        self.assertCountEqual(list(self.task.assigned_to.all()), updated_assigned_users)        
        self.assertNotIn(removed_user, self.task.assigned_to.all())

        # Retrieve Activity instances related to the task and assert messages
        activity_messages = [activity.message for activity in Activity.objects.filter(task=self.task)]
        expected_messages = [
            f"Task title was changed to {new_title}.",
            "Task description was changed.",
            f"Task status was changed to {new_status.title}.",
            f"Task start date was changed to {new_start_date}.",
            f"Task end date was changed to {new_end_date}.",
            f"Task assined to {self.user1}.",
            f"Task assined to {self.user2}.",
            f"{removed_user} removed from task assigness.",
        ]
        self.assertCountEqual(activity_messages, expected_messages)


    def test_get_comment(self):
        comments = self.task.get_comment()
        self.assertCountEqual(comments, [self.comment1, self.comment2])


    def test_get_attachments(self):
        attachment1 = Attachment.objects.create(file="attachment1.txt", task=self.task, owner=self.user1)
        attachment2 = Attachment.objects.create(file="attachment2.txt", task=self.task, owner=self.user2)
        attachments = self.task.get_attachments()
        self.assertCountEqual(attachments, [attachment1, attachment2])

    def test_get_activity(self):
        activity1 = Activity.objects.create(doer=self.user1, task=self.task, message="Activity 1")
        activity2 = Activity.objects.create(doer=self.user2, task=self.task, message="Activity 2")
        activities = self.task.get_activity()
        self.assertCountEqual(activities, [activity1, activity2])

    def test_get_assigned_users(self):
        user3 = User.objects.create(email="user3@example.com")
        user4 = User.objects.create(email="user4@example.com")
        self.task.assigned_to.add(self.user1, self.user2, user3)
        assigned_users = self.task.get_assigned_users()
        self.assertCountEqual(assigned_users, [self.user1, self.user2, user3])


    def test_get_task_comments(self):
        comments = self.task.get_task_comments()
        self.assertCountEqual(comments, [self.comment1, self.comment2])

    def test_get_task_comments_count(self):
        comment_count = self.task.get_task_comments_count()
        self.assertEqual(comment_count, 2)


class WorkSpaceTestCase(TestCase):
    
    def setUp(self) -> None:
        self.user_ata = User.objects.create_user(email='ata@gmail.COM', password='1234', first_name='ata', last_name='test', avatar=None, mobile='01234567890')
        self.user_ali = User.objects.create_user(email='ali@gmail.COM', password='1234', first_name='ali', last_name='test', mobile='01234567893')
        self.workspace_ata = WorkSpace.objects.create(title='Ata Workspace', owner=self.user_ata)
        self.workspace_ata.members.add(self.user_ali)
        self.workspace_ata_2 = WorkSpace.objects.create(title='New Workspace', owner=self.user_ata)
        self.board_ata_1_1 = Board.objects.create(title='Board One', work_space=self.workspace_ata)
        self.list_1_1_1 = TaskList.objects.create(title='List One', board= self.board_ata_1_1)
        self.task_1 = Task.objects.create(title='Task One', description='...', status=self.list_1_1_1, order=1)
        self.image = 'image.png'
       
        return super().setUp()

    def test_work_space(self):
        self.assertTrue(WorkSpace.objects.filter(title=self.workspace_ata.title, owner=self.workspace_ata.owner).exists())

    def test_str(self):
        self.assertEqual(str(self.workspace_ata), f'{self.workspace_ata.title} - owned by {self.workspace_ata.owner}')

    def test_add_member(self):
        w_member = self.workspace_ata.add_member(self.user_ali)
        self.assertEqual(w_member, self.workspace_ata)
        
        self.workspace_ata.clean()
        new_member = self.workspace_ata.add_member(self.user_ata)
        with self.assertRaises(ValidationError):
            self.workspace_ata.clean()


    def test_add_board(self):
        w_board = self.workspace_ata.add_board(title=self.board_ata_1_1.title, background_image=None)
        self.assertQuerysetEqual(w_board, self.workspace_ata.work_space_boards.filter(title=self.board_ata_1_1.title))

        w_board = self.workspace_ata.add_board(title=self.board_ata_1_1.title, background_image=self.image)
        self.assertQuerysetEqual(w_board, self.workspace_ata.work_space_boards.filter(title=self.board_ata_1_1.title))

    def test_work_space_members(self):
        self.assertQuerysetEqual(self.workspace_ata.work_space_members(), self.workspace_ata.members.all())

    def test_archive(self):
        self.assertTrue(self.workspace_ata.is_active)
        self.assertTrue(self.board_ata_1_1.is_active)
        self.assertTrue(self.list_1_1_1.is_active)
        self.assertTrue(self.task_1.is_active)

        self.workspace_ata.archive()
        self.assertFalse(self.workspace_ata.is_active)
        self.board_ata_1_1.refresh_from_db()
        self.assertFalse(self.board_ata_1_1.is_active)
        self.list_1_1_1.refresh_from_db()
        self.assertFalse(self.list_1_1_1.is_active)
        self.task_1.refresh_from_db()
        self.assertFalse(self.task_1.is_active)
    
    def test_restore(self):
        self.workspace_ata.archive()
        self.assertFalse(self.workspace_ata.is_active)
        self.board_ata_1_1.refresh_from_db()
        self.assertFalse(self.board_ata_1_1.is_active)
        self.list_1_1_1.refresh_from_db()
        self.assertFalse(self.list_1_1_1.is_active)
        self.task_1.refresh_from_db()
        self.assertFalse(self.task_1.is_active)

        self.workspace_ata.restore()
        self.assertTrue(self.workspace_ata.is_active)
        self.board_ata_1_1.refresh_from_db()
        self.assertTrue(self.board_ata_1_1.is_active)
        self.list_1_1_1.refresh_from_db()
        self.assertTrue(self.list_1_1_1.is_active)
        self.task_1.refresh_from_db()
        self.assertTrue(self.task_1.is_active)

class BoardTestCase(TestCase):

    def setUp(self) -> None:

        self.user_ata = User.objects.create_user(email='ata@gmail.COM', password='1234', first_name='ata', last_name='test', avatar=None, mobile='01234567890')        
        self.workspace_ata = WorkSpace.objects.create(title='Ata Workspace', owner=self.user_ata)
        self.board_ata_1_1 = Board.objects.create(title='Board One', work_space=self.workspace_ata)
        self.board_ata_1_2 = Board.objects.create(title='Board Two', work_space=self.workspace_ata)
        self.list_1_1_1 = TaskList.objects.create(title='List One', board= self.board_ata_1_1)
        self.task_1 = Task.objects.create(title='Task One', description='...', status=self.list_1_1_1, order=1)
        self.label_1 = Label.objects.create(title='Label one', board=self.board_ata_1_1)
        
        
        return super().setUp()

    def test_str(self):
        self.assertEqual(str(self.board_ata_1_1), f'{self.board_ata_1_1.title} - related work space: {self.board_ata_1_1.work_space}')

    def test_add_tasklist(self):
        b_tasklist = self.board_ata_1_2.add_tasklist(title='List Two')
        tasklist = self.board_ata_1_2.board_Tasklists.filter(title='List Two')
        self.assertEqual(b_tasklist, tasklist[0])

    def test_get_board_labels(self):
        board_labels = self.board_ata_1_1.get_board_labels()
        self.assertCountEqual(board_labels, self.board_ata_1_1.board_labels.all())

    def test_get_status_choices(self):
        choices = self.board_ata_1_1.get_status_choices()
        titles = self.board_ata_1_1.board_Tasklists.all()
        self.assertQuerysetEqual(choices, titles)


    def test_archive(self):
        self.assertTrue(self.board_ata_1_1.is_active)
        self.assertTrue(self.list_1_1_1.is_active)
        self.assertTrue(self.task_1.is_active)

        self.board_ata_1_1.archive()
        self.assertFalse(self.board_ata_1_1.is_active)
        self.list_1_1_1.refresh_from_db()
        self.assertFalse(self.list_1_1_1.is_active)
        self.task_1.refresh_from_db()
        self.assertFalse(self.task_1.is_active)
    
    def test_restore(self):
        self.board_ata_1_1.archive()
        self.assertFalse(self.board_ata_1_1.is_active)
        self.list_1_1_1.refresh_from_db()
        self.assertFalse(self.list_1_1_1.is_active)
        self.task_1.refresh_from_db()
        self.assertFalse(self.task_1.is_active)

        self.board_ata_1_1.restore()
        self.assertTrue(self.board_ata_1_1.is_active)
        self.list_1_1_1.refresh_from_db()
        self.assertTrue(self.list_1_1_1.is_active)
        self.task_1.refresh_from_db()
        self.assertTrue(self.task_1.is_active)
   
class TaskListTestCase(TestCase):

    def setUp(self) -> None:

        self.user_ata = User.objects.create_user(email='ata@gmail.COM', password='1234', first_name='ata', last_name='test', avatar=None, mobile='01234567890')        
        self.workspace_ata = WorkSpace.objects.create(title='Ata Workspace', owner=self.user_ata)
        self.board_ata_1_1 = Board.objects.create(title='Board One', work_space=self.workspace_ata)
        self.list_1_1_1 = TaskList.objects.create(title='List One', board= self.board_ata_1_1)
        self.list_1_1_2 = TaskList.objects.create(title='List Two', board= self.board_ata_1_1)
        self.task_1 = Task.objects.create(title='Task One', description='...', status=self.list_1_1_1, order=1)
        self.task_1.assigned_to.add(self.user_ata)
        
        return super().setUp()

    def test_str(self):
        self.assertEqual(str(self.list_1_1_1), f'{self.list_1_1_1.title} - related board: {self.list_1_1_1.board}')

    def test_add_task(self):
        l_task = self.list_1_1_2.add_task(doer=self.user_ata, title='Task Two', description='...')
        task = self.list_1_1_2.status_tasks.filter(title='Task Two')  
        self.assertEqual(l_task, task[0])

    def test_task_count(self):
        self.assertEqual(self.list_1_1_1.task_count(), self.list_1_1_1.status_tasks.all().count())

    def test_archive(self):
        self.assertTrue(self.list_1_1_1.is_active)
        self.assertTrue(self.task_1.is_active)

        self.list_1_1_1.archive()
        self.assertFalse(self.list_1_1_1.is_active)
        self.task_1.refresh_from_db()
        self.assertFalse(self.task_1.is_active)
    
    def test_restore(self):
        self.list_1_1_1.archive()
        self.assertFalse(self.list_1_1_1.is_active)
        self.task_1.refresh_from_db()
        self.assertFalse(self.task_1.is_active)

        self.list_1_1_1.restore()
        self.assertTrue(self.list_1_1_1.is_active)
        self.task_1.refresh_from_db()
        self.assertTrue(self.task_1.is_active)

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
        attachment = Attachment.objects.create(file='testfile.pdf', task=self.task, owner=self.user)
        message = f"{self.user} attached a new file."
        attachment_activity = Activity.objects.create(task=self.task, doer=self.user, message=message)
        activities = Activity.attachment_activity_on_board(self.board)
        self.assertEqual(activities.count(), 1)  
        self.assertEqual(activities.first(), attachment_activity)

    def test_task_create_activity_on_board(self):
        message = f"{self.user} created a new task."
        task_create_activity = Activity.objects.create(task=self.task, doer=self.user, message=message)
        activities = Activity.task_create_activity_on_board(self.board)
        self.assertEqual(activities.count(), 1)  
        self.assertEqual(activities.first(), task_create_activity)  

    def test_from_to_date_on_board(self):
        from_date = datetime(2023, 1, 1)
        to_date = datetime(2023, 1, 3)
        activity1 = Activity.objects.create(doer=self.user, message='activity 1', task=self.task)
        activity1.create_at = from_date + timedelta(days=1)
        activity1.save()
        activity2 = Activity.objects.create(doer=self.user, message='activity 2', task=self.task)
        activity2.create_at = from_date + timedelta(days=2)
        activity2.save()
        activity_outside_range = Activity.objects.create(doer=self.user, message='activity outside range', task=self.task)
        activity_outside_range.create_at = to_date + timedelta(days=1)
        activity_outside_range.save()
        activities = Activity.from_to_date_on_board(from_date, to_date, self.board)
        self.assertIn(activity1, activities)
        self.assertIn(activity2, activities)
        self.assertNotIn(activity_outside_range, activities)


    def test_doer_other_activitys_on_board(self):
        another_activity = Activity.objects.create(doer=self.user, message='another test', task=self.task)
        related_activities = self.activity.doer_other_activitys_on_board()
        related_activities = related_activities.exclude(id=self.activity.id)
        self.assertIn(another_activity, related_activities)
        self.assertNotIn(self.activity, related_activities)
   

    def test_str(self):
        activity_str = str(self.activity)
        expected_str = f'Done By {self.user}'
        self.assertEqual(activity_str, expected_str)




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
        file = 'newfile.pdf'
        task = self.task
        owner = self.user
        attachment = Attachment.create(file=file, task=task, owner=owner)
        self.assertEqual(attachment.file, file)
        self.assertEqual(attachment.task, task)
        self.assertEqual(attachment.owner, owner)
        message = f"{owner} attached a new file."
        activity = Activity.objects.filter(task=task, doer=owner, message=message).first()
        self.assertIsNotNone(activity)


    def test_owner_other_attachments_on_board(self):
        attachment1 = Attachment.objects.create(file='testfile1.pdf', task=self.task, owner=self.user)
        attachment2 = Attachment.objects.create(file='testfile2.pdf', task=self.task, owner=self.user)
        
        attachments = self.attachment.owner_other_attachments_on_board()
        
        self.assertEqual(attachments.count(), 3)  # Check if there are 3 attachments
        self.assertTrue(all(a.owner == self.user for a in attachments))  # Check ownership
        
        expected_board = self.attachment.task.status.board
        self.assertTrue(all(a.task.status.board == expected_board for a in attachments))


    def test_archive(self):
        attachment = Attachment.objects.create(file='testfile.pdf', task=self.task, owner=self.user)
        
        self.assertTrue(attachment.is_active)  
        
        attachment.archive()
        
        self.assertFalse(attachment.is_active) 
        activity = Activity.objects.get(task=self.task, doer=self.user)
        self.assertEqual(activity.message, f"{self.user} deleted a attachment on task {self.task.title}.")
        

        attachment.restore()
        self.assertTrue(attachment.is_active)  


    def test_attachment_str(self):
        attachment_str = str(self.attachment)
        expected_str = f"Attached by {self.user}."
        self.assertEqual(attachment_str, expected_str)
        
