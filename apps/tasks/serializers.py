from rest_framework import serializers

from apps.tasks.models import Category, Task, TaskShare
from apps.users.models import User


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(trim_whitespace=False)

    class Meta:
        model = Category
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("O nome da categoria não pode ser vazio.")

        owner = self.context["request"].user
        qs = Category.objects.filter(owner=owner, name__iexact=value)

        # Exclui o próprio objeto em caso de update
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Você já possui uma categoria com este nome.")

        return value

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    title = serializers.CharField(trim_whitespace=False)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        required=False,
        allow_null=True,
    )
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_shared = serializers.SerializerMethodField()
    origin = serializers.SerializerMethodField()
    due_date = serializers.DateField(
        format="%Y-%m-%d",
        input_formats=["%Y-%m-%d"],
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "is_completed",
            "priority",
            "due_date",
            "category_id",
            "category_name",
            "is_shared",
            "origin",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_shared", "created_at", "updated_at"]

    def get_is_shared(self, obj):
        return obj.shares.exists()

    def validate_category_id(self, category):
        """Garante que o usuário só usa categorias próprias."""
        if category and category.owner != self.context["request"].user:
            raise serializers.ValidationError("Categoria inválida.")
        return category

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("O título não pode ser vazio.")
        return value

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)

    def get_origin(self, obj):
        request = self.context.get("request")
        if not request:
            return "own"

        if obj.owner == request.user:
            return {"type": "own"}

        return {
            "type": "shared",
            "shared_by": obj.owner.email,  # ou .name, dependendo do seu modelo de User
        }


class TaskShareSerializer(serializers.ModelSerializer):
    shared_with_id = serializers.UUIDField(write_only=True)
    shared_with = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TaskShare
        fields = ["id", "shared_with", "shared_with_id", "created_at"]
        read_only_fields = ["id", "shared_with", "created_at"]

    def validate_shared_with_id(self, value):
        request = self.context["request"]

        if value == request.user.id:
            raise serializers.ValidationError("Você não pode compartilhar uma tarefa com você mesmo.")

        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado.")

        self._shared_with_user = user
        return value

    def validate(self, attrs):
        task = self.context["task"]
        if TaskShare.objects.filter(task=task, shared_with=self._shared_with_user).exists():
            raise serializers.ValidationError("Esta tarefa já foi compartilhada com este usuário.")
        return attrs

    def create(self, validated_data):
        validated_data.pop("shared_with_id")
        validated_data["shared_with"] = self._shared_with_user
        validated_data["task"] = self.context["task"]
        return super().create(validated_data)
