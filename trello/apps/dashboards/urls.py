from rest_framework import routers
from .views.board_views import BoardModelViewSet

app_name = 'dashboards'
urlpatterns = []

router = routers.DefaultRouter()
# router.register(prefix='' ,viewset=...ViewSet)
# router.register(prefix='' ,viewset=...ViewSet)
# router.register(prefix='' ,viewset=...ViewSet)
router.register(r'board-viewset', BoardModelViewSet)

urlpatterns += router.urls




