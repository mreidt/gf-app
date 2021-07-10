from django.urls import path, include
from rest_framework.routers import DefaultRouter

from operation import views

router = DefaultRouter()
router.register('accounttype', views.AccountTypeViewSet)
router.register('account', views.AccountViewSet)
router.register('tag', views.TagViewSet)
router.register('operation', views.OperationViewSet)

app_name = 'operation'

urlpatterns = [
    path('', include(router.urls))
]
