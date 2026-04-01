from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.serializers import RegisterSerializer

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_with_normalized_email_and_hashed_password(self):
        user = User.objects.create_user(
            email="TEST@Example.COM",
            password="StrongPass123!",
            first_name="Celso",
        )

        self.assertEqual(user.email, "TEST@example.com")
        self.assertEqual(user.first_name, "Celso")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertNotEqual(user.password, "StrongPass123!")

    def test_create_user_without_email_raises_error(self):
        with self.assertRaisesMessage(ValueError, "O campo email é obrigatório."):
            User.objects.create_user(email="", password="StrongPass123!")

    def test_create_superuser_sets_required_flags(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="StrongPass123!",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser_requires_is_staff_true(self):
        with self.assertRaisesMessage(ValueError, "Superuser precisa de is_staff=True."):
            User.objects.create_superuser(
                email="admin@example.com",
                password="StrongPass123!",
                is_staff=False,
            )

    def test_create_superuser_requires_is_superuser_true(self):
        with self.assertRaisesMessage(ValueError, "Superuser precisa de is_superuser=True."):
            User.objects.create_superuser(
                email="admin@example.com",
                password="StrongPass123!",
                is_superuser=False,
            )


class RegisterSerializerTests(TestCase):
    def test_serializer_normalizes_email_and_trims_first_name(self):
        serializer = RegisterSerializer(
            data={
                "email": " USER@Example.COM ",
                "first_name": "  Celso  ",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.email, "user@example.com")
        self.assertEqual(user.first_name, "Celso")
        self.assertTrue(user.check_password("StrongPass123!"))

    def test_serializer_rejects_duplicate_email(self):
        User.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
            first_name="Celso",
        )

        serializer = RegisterSerializer(
            data={
                "email": "user@example.com",
                "first_name": "Maria",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_serializer_rejects_first_name_with_only_spaces(self):
        serializer = RegisterSerializer(
            data={
                "email": "user@example.com",
                "first_name": "   ",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["first_name"][0], "O nome não pode ser vazio.")

    def test_serializer_rejects_first_name_with_non_letters(self):
        serializer = RegisterSerializer(
            data={
                "email": "user@example.com",
                "first_name": "Celso 123",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["first_name"][0], "O nome deve conter apenas letras.")

    def test_serializer_rejects_password_mismatch(self):
        serializer = RegisterSerializer(
            data={
                "email": "user@example.com",
                "first_name": "Celso",
                "password": "StrongPass123!",
                "password_confirm": "AnotherPass123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["password"][0], "As senhas não coincidem.")


class UserApiTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.me_url = reverse("me")

    def test_register_creates_user_and_returns_public_data(self):
        response = self.client.post(
            self.register_url,
            {
                "email": "user@example.com",
                "first_name": "Celso",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "user@example.com")
        self.assertEqual(response.data["first_name"], "Celso")
        self.assertNotIn("password", response.data)
        self.assertNotIn("password_confirm", response.data)
        self.assertTrue(User.objects.filter(email="user@example.com").exists())

    def test_register_returns_validation_errors_for_invalid_payload(self):
        response = self.client.post(
            self.register_url,
            {
                "email": "user@example.com",
                "first_name": "Celso1",
                "password": "12345678",
                "password_confirm": "87654321",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)
        self.assertIn("password", response.data)

    def test_login_returns_jwt_tokens_for_valid_credentials(self):
        User.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
            first_name="Celso",
        )

        response = self.client.post(
            self.login_url,
            {"email": "user@example.com", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_me_requires_authentication(self):
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_authenticated_user_data(self):
        user = User.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
            first_name="Celso",
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], user.email)
        self.assertEqual(response.data["first_name"], user.first_name)
        self.assertIn("created_at", response.data)
