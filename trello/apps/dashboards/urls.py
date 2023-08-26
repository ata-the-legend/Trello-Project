from rest_framework import routers
from trello.apps.dashboards.views.label_views import LabelViewSet

app_name = 'dashboards'
urlpatterns = []

router = routers.DefaultRouter()
router.register(prefix='labels' ,viewset=LabelViewSet)
# router.register(prefix='' ,viewset=...ViewSet)
# router.register(prefix='' ,viewset=...ViewSet)

urlpatterns += router.urls




