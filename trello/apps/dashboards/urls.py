from rest_framework import routers
from trello.apps.dashboards.views import workspace_views , task_views, attachment_views

app_name = 'dashboards'
urlpatterns = []

router = routers.DefaultRouter()
router.register(prefix='attachment' ,viewset=attachment_views.AttachmentViewSet)
router.register(prefix='workspaces' ,viewset=workspace_views.WorkspaceViewSet)
router.register(prefix='tasks' ,viewset=task_views.TaskViewSet)

urlpatterns += router.urls




