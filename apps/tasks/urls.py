from rest_framework.routers import DefaultRouter

from apps.tasks import views

router = DefaultRouter()
router.register("categories", views.CategoryViewSet, basename="category")
router.register("", views.TaskViewSet, basename="task")

urlpatterns = router.urls
