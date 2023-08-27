from rest_framework import routers
from trello.apps.dashboards.views.comment_views import CommentViewSet

app_name = 'dashboards'
urlpatterns = []

router = routers.DefaultRouter()
router.register(prefix='comments' ,viewset=CommentViewSet )
# router.register(prefix='' ,viewset=...ViewSet)
# router.register(prefix='' ,viewset=...ViewSet)

urlpatterns += router.urls




