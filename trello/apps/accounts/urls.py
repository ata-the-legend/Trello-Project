from django.urls import path
from .routers import UserCustomRouter
from .views import UserView


app_name = 'accounts'
urlpatterns = []


router = UserCustomRouter()
router.register(prefix='' ,viewset=UserView)
urlpatterns += router.urls
