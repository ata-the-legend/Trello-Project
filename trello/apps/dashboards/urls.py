from rest_framework import routers
from trello.apps.dashboards.views.attachment_views import AttachmentViewSet

app_name = 'dashboards'
urlpatterns = []

router = routers.DefaultRouter()
router.register(prefix='attachment' ,viewset=AttachmentViewSet)
# router.register(prefix='' ,viewset=...ViewSet)
# router.register(prefix='' ,viewset=...ViewSet)

urlpatterns += router.urls




