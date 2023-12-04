from django.urls import include, path
from rest_framework.routers import SimpleRouter

from order.views import LoginUser, OrderViewSet

router = SimpleRouter()
router.register('', OrderViewSet)


urlpatterns = [
    path('auth/login/', LoginUser.as_view(), name='login-user'),
    path('orders/', include(router.urls)),
]
