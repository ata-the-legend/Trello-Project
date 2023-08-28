from rest_framework import routers
from trello.apps.dashboards.views import workspace_views 

app_name = 'dashboards'
urlpatterns = []

router = routers.DefaultRouter()
# router.register(prefix='' ,viewset=...ViewSet)
router.register(prefix='workspaces' ,viewset=workspace_views.WorkspaceViewSet)
# router.register(prefix='' ,viewset=...ViewSet)

urlpatterns += router.urls




