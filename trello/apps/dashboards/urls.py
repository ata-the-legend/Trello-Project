from rest_framework import routers
from trello.apps.dashboards.views import comment_views 

app_name = 'dashboards'
urlpatterns = []

router = routers.DefaultRouter()
router.register(prefix='comments' ,viewset=comment_views.CommentViewSet)
# router.register(prefix='' ,viewset=...ViewSet)
# router.register(prefix='' ,viewset=...ViewSet)

urlpatterns += router.urls




