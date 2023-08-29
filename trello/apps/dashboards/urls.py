from rest_framework import routers
from trello.apps.dashboards.views import workspace_views, tasklist_views, task_views, board_views, attachment_views, label_views


app_name = 'dashboards'
urlpatterns = []

router = routers.DefaultRouter()
router.register(prefix='labels' ,viewset=label_views.LabelViewSet)
router.register(prefix='attachment' ,viewset=attachment_views.AttachmentViewSet)
router.register(prefix='boards', viewset=board_views.BoardModelViewSet)
router.register(prefix='workspaces' ,viewset=workspace_views.WorkspaceViewSet)
router.register(prefix='tasks' ,viewset=task_views.TaskViewSet)
router.register(prefix='tasklists' ,viewset=tasklist_views.TaskListModelViewSet)

urlpatterns += router.urls




