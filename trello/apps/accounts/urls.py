from django.urls import path
from .routers import UserCustomRouter
from .views import UserApiView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView


app_name = 'accounts'
urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
]


router = UserCustomRouter()
router.register(prefix='' ,viewset=UserApiView)
urlpatterns += router.urls
