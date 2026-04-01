# apps/tasks/views.py
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.tasks.models import Category, Task
from apps.tasks.serializers import CategorySerializer, TaskSerializer, TaskShareSerializer


class CategoryViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        """Usuário só vê suas próprias categorias."""
        queryset = Category.objects.filter(owner=self.request.user)

        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

class TaskViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "priority"]

    def get_queryset(self):
        """Retorna tarefas próprias e compartilhadas, com filtros opcionais."""
        user = self.request.user

        own = Task.objects.filter(owner=user)
        shared = Task.objects.filter(shares__shared_with=user)
        queryset = (own | shared).distinct()

        is_completed = self.request.query_params.get("is_completed")
        priority = self.request.query_params.get("priority")
        category_id = self.request.query_params.get("category_id")

        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == "true")
        if priority:
            queryset = queryset.filter(priority=priority)
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    @action(detail=True, methods=["patch"], url_path="toggle")
    def toggle_completed(self, request, pk=None):
        """Alterna o status de conclusão da tarefa."""
        task = self.get_object()

        if task.owner != request.user:
            return Response(
                {"detail": "Apenas o dono pode alterar o status."},
                status=status.HTTP_403_FORBIDDEN,
            )

        task.is_completed = not task.is_completed
        task.save(update_fields=["is_completed", "updated_at"])
        return Response(TaskSerializer(task, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="share")
    def share(self, request, pk=None):
        """Compartilha a tarefa com outro usuário."""
        task = self.get_object()

        if task.owner != request.user:
            return Response(
                {"detail": "Apenas o dono pode compartilhar a tarefa."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskShareSerializer(
            data=request.data,
            context={"request": request, "task": task},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)