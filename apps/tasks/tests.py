from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from apps.tasks.models import Category, Task, TaskShare
from apps.tasks.serializers import CategorySerializer, TaskSerializer, TaskShareSerializer


User = get_user_model()


class CategorySerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123!",
            first_name="Owner",
        )

    def get_request(self):
        request = self.factory.post("/api/v1/tasks/categories/")
        request.user = self.user
        return request

    def test_rejects_empty_name_after_trim(self):
        serializer = CategorySerializer(
            data={"name": "   "},
            context={"request": self.get_request()},
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["name"][0], "O nome da categoria não pode ser vazio.")

    def test_rejects_duplicate_name_case_insensitive(self):
        Category.objects.create(owner=self.user, name="Trabalho")

        serializer = CategorySerializer(
            data={"name": " trabalho "},
            context={"request": self.get_request()},
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["name"][0], "Você já possui uma categoria com este nome.")

    def test_create_assigns_owner(self):
        serializer = CategorySerializer(
            data={"name": "Estudos"},
            context={"request": self.get_request()},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        category = serializer.save()

        self.assertEqual(category.owner, self.user)
        self.assertEqual(category.name, "Estudos")


class TaskSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123!",
            first_name="Owner",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="StrongPass123!",
            first_name="Other",
        )
        self.category = Category.objects.create(owner=self.user, name="Pessoal")
        self.other_category = Category.objects.create(owner=self.other_user, name="Outro")

    def get_request(self):
        request = self.factory.post("/api/v1/tasks/")
        request.user = self.user
        return request

    def test_rejects_blank_title_after_trim(self):
        serializer = TaskSerializer(
            data={"title": "   "},
            context={"request": self.get_request()},
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["title"][0], "O título não pode ser vazio.")

    def test_rejects_category_from_another_user(self):
        serializer = TaskSerializer(
            data={
                "title": "Comprar café",
                "priority": Task.Priority.MEDIUM,
                "category_id": str(self.other_category.id),
            },
            context={"request": self.get_request()},
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["category_id"][0], "Categoria inválida.")

    def test_create_assigns_owner_and_category(self):
        serializer = TaskSerializer(
            data={
                "title": "Comprar café",
                "description": "No mercado",
                "priority": Task.Priority.HIGH,
                "category_id": str(self.category.id),
            },
            context={"request": self.get_request()},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        task = serializer.save()

        self.assertEqual(task.owner, self.user)
        self.assertEqual(task.category, self.category)
        self.assertEqual(task.priority, Task.Priority.HIGH)

    def test_is_shared_returns_true_when_task_has_share(self):
        task = Task.objects.create(owner=self.user, title="Comprar café")
        TaskShare.objects.create(task=task, shared_with=self.other_user)

        serializer = TaskSerializer(task, context={"request": self.get_request()})

        self.assertTrue(serializer.data["is_shared"])


class TaskShareSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123!",
            first_name="Owner",
        )
        self.target_user = User.objects.create_user(
            email="friend@example.com",
            password="StrongPass123!",
            first_name="Friend",
        )
        self.task = Task.objects.create(owner=self.owner, title="Revisar relatório")

    def get_request(self):
        request = self.factory.post("/api/v1/tasks/share/")
        request.user = self.owner
        return request

    def test_rejects_share_with_self(self):
        serializer = TaskShareSerializer(
            data={"shared_with_email": "owner@example.com"},
            context={"request": self.get_request(), "task": self.task},
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["shared_with_email"][0],
            "Você não pode compartilhar uma tarefa com você mesmo.",
        )

    def test_rejects_share_with_unknown_user(self):
        serializer = TaskShareSerializer(
            data={"shared_with_email": "missing@example.com"},
            context={"request": self.get_request(), "task": self.task},
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["shared_with_email"][0], "Usuário não encontrado.")

    def test_rejects_duplicate_share(self):
        TaskShare.objects.create(task=self.task, shared_with=self.target_user)

        serializer = TaskShareSerializer(
            data={"shared_with_email": "friend@example.com"},
            context={"request": self.get_request(), "task": self.task},
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "Esta tarefa já foi compartilhada com este usuário.",
        )

    def test_create_resolves_shared_user_from_email(self):
        serializer = TaskShareSerializer(
            data={"shared_with_email": "friend@example.com"},
            context={"request": self.get_request(), "task": self.task},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        share = serializer.save()

        self.assertEqual(share.task, self.task)
        self.assertEqual(share.shared_with, self.target_user)


class TaskApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123!",
            first_name="Owner",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="StrongPass123!",
            first_name="Other",
        )
        self.third_user = User.objects.create_user(
            email="third@example.com",
            password="StrongPass123!",
            first_name="Third",
        )
        self.category = Category.objects.create(owner=self.user, name="Trabalho")
        self.other_category = Category.objects.create(owner=self.other_user, name="Pessoal")

        self.category_list_url = reverse("category-list")
        self.task_list_url = reverse("task-list")

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)

    def test_category_list_returns_only_authenticated_user_categories(self):
        Category.objects.create(owner=self.other_user, name="Saude")
        self.authenticate()

        response = self.client.get(self.category_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Trabalho")

    def test_category_create_sets_owner(self):
        self.authenticate()

        response = self.client.post(
            self.category_list_url,
            {"name": "Estudos"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(owner=self.user, name="Estudos").exists())

    def test_task_list_returns_own_and_shared_tasks(self):
        own_task = Task.objects.create(owner=self.user, title="Minha tarefa")
        shared_task = Task.objects.create(owner=self.other_user, title="Compartilhada")
        TaskShare.objects.create(task=shared_task, shared_with=self.user)
        Task.objects.create(owner=self.third_user, title="Invisível")
        self.authenticate()

        response = self.client.get(self.task_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_titles = {item["title"] for item in response.data["results"]}
        self.assertEqual(returned_titles, {own_task.title, shared_task.title})

    def test_task_list_filters_by_completion_priority_and_category(self):
        Task.objects.create(
            owner=self.user,
            title="Concluída",
            is_completed=True,
            priority=Task.Priority.HIGH,
            category=self.category,
        )
        Task.objects.create(
            owner=self.user,
            title="Pendente",
            is_completed=False,
            priority=Task.Priority.LOW,
        )
        self.authenticate()

        response = self.client.get(
            self.task_list_url,
            {
                "is_completed": "true",
                "priority": Task.Priority.HIGH,
                "category_id": str(self.category.id),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Concluída")

    def test_task_create_rejects_category_from_another_user(self):
        self.authenticate()

        response = self.client.post(
            self.task_list_url,
            {
                "title": "Nova tarefa",
                "priority": Task.Priority.MEDIUM,
                "category_id": str(self.other_category.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["category_id"][0], "Categoria inválida.")

    def test_task_create_sets_owner(self):
        self.authenticate()

        response = self.client.post(
            self.task_list_url,
            {
                "title": "Nova tarefa",
                "description": "Detalhes",
                "priority": Task.Priority.MEDIUM,
                "category_id": str(self.category.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(title="Nova tarefa")
        self.assertEqual(task.owner, self.user)
        self.assertEqual(task.category, self.category)

    def test_toggle_completed_updates_owner_task(self):
        task = Task.objects.create(owner=self.user, title="Alternar")
        self.authenticate()

        response = self.client.patch(reverse("task-toggle-completed", args=[task.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertTrue(task.is_completed)

    def test_toggle_completed_forbidden_for_shared_user(self):
        task = Task.objects.create(owner=self.other_user, title="Compartilhada")
        TaskShare.objects.create(task=task, shared_with=self.user)
        self.authenticate()

        response = self.client.patch(reverse("task-toggle-completed", args=[task.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "Apenas o dono pode alterar o status.")

    def test_share_creates_share_for_owner(self):
        task = Task.objects.create(owner=self.user, title="Compartilhar")
        self.authenticate()

        response = self.client.post(
            reverse("task-share", args=[task.id]),
            {"shared_with_email": "other@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TaskShare.objects.filter(task=task, shared_with=self.other_user).exists())

    def test_share_forbidden_for_non_owner(self):
        task = Task.objects.create(owner=self.other_user, title="Compartilhada")
        TaskShare.objects.create(task=task, shared_with=self.user)
        self.authenticate()

        response = self.client.post(
            reverse("task-share", args=[task.id]),
            {"shared_with_email": "third@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "Apenas o dono pode compartilhar a tarefa.")
