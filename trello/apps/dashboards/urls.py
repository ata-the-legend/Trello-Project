from rest_framework import routers
from trello.apps.dashboards.views import workspace_views, board_views

app_name = 'dashboards'
urlpatterns = []

router = routers.DefaultRouter()
# router.register(prefix='' ,viewset=...ViewSet)
# router.register(prefix='' ,viewset=...ViewSet)
router.register(prefix='boards', viewset=board_views.BoardModelViewSet)

urlpatterns += router.urls




