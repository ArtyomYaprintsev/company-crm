from django.urls import include, path, re_path
from rest_framework.routers import SimpleRouter

from order import views

router = SimpleRouter()
router.register('', views.OrderViewSet)


urlpatterns = [
    re_path(r'^service/', views.service,),
    path('auth/login/', views.LoginUser.as_view(), name='login-user'),
    path('auth/personal/', views.ClientPersonalView.as_view()),
    path('orders/properties/', views.OrderPropertiesView.as_view()),
    path('orders/', include(router.urls)),
]
