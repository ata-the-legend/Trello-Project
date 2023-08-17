from django.urls import path
from .routers import UserCustomRouter
from .views import UserView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


app_name = 'accounts'
urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


router = UserCustomRouter()
router.register(prefix='' ,viewset=UserView)
urlpatterns += router.urls