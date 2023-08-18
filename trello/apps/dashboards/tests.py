from django.utils import timezone
from datetime import datetime, timedelta, timezone
from django.test import TestCase 
from django.contrib.auth import get_user_model
from trello.apps.dashboards.models import Label, Board ,WorkSpace,Task,TaskList ,Comment , Activity,Attachment


User = get_user_model()

class LabelTestCase(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(password="testpassword", email="testuser@example.com")
        self.test_workspace = WorkSpace.objects.create(title="Test Workspace", owner=self.test_user)
        self.test_board = Board.objects.create(title="Test Board", work_space=self.test_workspace)
        

    def test_create_label(self):
        label_title = "Test Label"
        label = Label.create_label(title=label_title, board=self.test_board)
        
        
        self.assertIsInstance(label, Label)
        self.assertEqual(str(label), label_title)
        self.assertEqual(label.title, label_title)
        self.assertEqual(label.board, self.test_board)
        
        saved_label = Label.objects.get(title=label_title, board=self.test_board)
        self.assertEqual(label, saved_label)

    def test_get_label_choices(self):
        label_titles = ["Label 1", "Label 2", "Label 3"]
        for title in label_titles:
            Label.create_label(title=title, board=self.test_board)

        label_choices = Label.get_label_choices()

        self.assertEqual(len(label_choices), len(label_titles))
        for label_title in label_titles:
            self.assertIn(label_title, label_choices)

    def test_get_tasks(self):
        label_title = "Test Label"
        label = Label.create_label(title=label_title, board=self.test_board)

        task_titles = ["Task 1", "Task 2", "Task 3"]
        tasks = []
        for title in task_titles:
            task_list = TaskList.objects.create(title="Test TaskList", board=self.test_board)
            task = Task.objects.create(title=title, description="Test description", status=task_list)
            task.labels.add(label)
            tasks.append(task)
        label_tasks = label.get_tasks()
        self.assertEqual(len(label_tasks), len(task_titles))
        for task_title in task_titles:
            self.assertTrue(any(task.title == task_title for task in label_tasks))


    def test_get_task_count(self):
        label_title = "Test Label"
        label = Label.create_label(title=label_title, board=self.test_board)
        task_titles = ["Task 1", "Task 2", "Task 3"]
        for title in task_titles:
            task_list = TaskList.objects.create(title="Test TaskList", board=self.test_board)
            task = Task.objects.create(title=title, description="Test description", status=task_list)
            task.labels.add(label)
        task_count = label.get_task_count()
        self.assertEqual(task_count, len(task_titles))



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
        self.assertEqual(activity.message, f"{self.user.get_full_name()} replied to a comment on task {self.task.title}.")
        created_comment_without_parent = Comment.create_comment(body='Another Test Comment', task=self.task, author=self.user)
        self.assertEqual(created_comment_without_parent.body, 'Another Test Comment')
        self.assertEqual(created_comment_without_parent.task, self.task)
        self.assertEqual(created_comment_without_parent.author, self.user)
        self.assertIsNone(created_comment_without_parent.parent)
        activity_without_parent = Activity.objects.last()
        self.assertEqual(activity_without_parent.task, self.task)
        self.assertEqual(activity_without_parent.doer, self.user)
        self.assertEqual(activity_without_parent.message, f"{self.user.get_full_name()} added a new comment on task {self.task.title}.")
        


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
            labels=[self.label1, self.label2],
            start_date=datetime.strptime("2023-01-01", "%Y-%m-%d"),  # Convert to datetime
            end_date=datetime.strptime("2023-12-31", "%Y-%m-%d"),    # Convert to datetime
            assigned_to=[self.user1, self.user2]
        )
        self.assertEqual(task.start_date.strftime('%Y-%m-%d'), "2023-01-01")
        self.assertEqual(task.end_date.strftime('%Y-%m-%d'), "2023-12-31")
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertEqual(task.status, self.task_list)
        self.assertCountEqual(task.labels.all(), [self.label1, self.label2])
        self.assertCountEqual(task.assigned_to.all(), [self.user1, self.user2])



    def test_update_task(self):
        new_title = "Updated Title"
        new_description = "Updated Description"
        new_status = self.task_list  # Update with a valid TaskList instance
        new_order = 2
        new_labels = [self.label1, self.label2]  # Update with valid Label instances
        new_start_date = datetime(2023, 8, 1, tzinfo=timezone.utc)
        new_end_date = datetime(2023, 8, 15, tzinfo=timezone.utc)
        new_assigned_to = [self.user1, self.user2]

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
            f"Task assined to {self.user1.get_full_name()}.",
            f"Task assined to {self.user2.get_full_name()}.",
            f"{removed_user.get_full_name()} removed from task assigness.",
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