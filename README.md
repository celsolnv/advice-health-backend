# Advice Health — API To-Do List

API REST para aplicação de lista de tarefas: cadastro e autenticação de usuários, CRUD de tarefas e categorias, compartilhamento entre usuários, filtros, busca e paginação. Projeto desenvolvido como teste técnico, com foco em organização, segurança por padrão (JWT) e testes automatizados.

## Tecnologias

| Camada | Tecnologia |
|--------|------------|
| Linguagem | Python 3.11 |
| Framework | Django 5.2 |
| API | Django REST Framework |
| Autenticação | JWT (djangorestframework-simplejwt) |
| Banco de dados | PostgreSQL 15 (via Docker) |
| CORS | django-cors-headers |
| Configuração | python-dotenv |
| Testes | pytest, pytest-django, Selenium |
| Qualidade | flake8, black, isort |

## Arquitetura do projeto

```
backend/
├── core/                    # Projeto Django (settings, URLs raiz, exceções)
│   └── settings/
│       ├── base.py          # Configuração comum (DRF, JWT, DB, apps)
│       ├── development.py   # Dev (DEBUG, CORS para frontend local)
│       ├── production.py    # Produção (validações de SECRET_KEY / ALLOWED_HOSTS)
│       └── test.py          # SQLite em memória para testes pytest
├── apps/
│   ├── users/               # Usuário customizado, registro, login, perfil, busca de usuários
│   └── tasks/               # Categorias, tarefas, compartilhamento (TaskShare)
├── requirements/
│   ├── base.txt             # Dependências de runtime
│   ├── development.txt      # Dev + testes + ferramentas
│   └── production.txt       # Produção
├── tests/e2e/               # Testes de ponta a ponta (pytest + Selenium)
├── docker-compose.yml       # PostgreSQL + serviço web
├── Dockerfile
├── manage.py
└── pytest.ini
```

**Convenções:** rotas versionadas em `/api/v1/`; apps de domínio em `apps/`; modelo de usuário customizado (`AUTH_USER_MODEL`).

## Pré-requisitos

- Python 3.11
- [Docker](https://docs.docker.com/get-docker/) e Docker Compose
- Cliente HTTP (curl, HTTPie, Postman, etc.) para explorar a API

## Como rodar localmente

### 1. Subir com Docker Compose (recomendado)

```bash
docker compose up --build
```

Isso sobe o banco PostgreSQL e a aplicação. A API ficará disponível em `http://localhost:8000`.

### 2. Apenas o banco via Docker (para desenvolvimento com venv local)

```bash
docker compose up -d db
```

O serviço `db` publica a porta **5433** no host (mapeamento `5433:5432`). Ajuste `DB_PORT` no `.env` conforme a tabela abaixo.

### 3. Backend com ambiente virtual

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
# ou: venv\Scripts\activate no Windows

pip install --upgrade pip
pip install -r requirements/development.txt
```

Copie e edite as variáveis de ambiente:

```bash
cp .env.example .env
```

Configure o `.env` para apontar para o Postgres do Docker:

| Variável | Exemplo |
|----------|---------|
| `DB_NAME` | `advice_health_db` |
| `DB_USER` | `postgres` |
| `DB_PASSWORD` | `postgres` |
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5433` |

## Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `DEBUG` | Ativa modo de depuração |
| `SECRET_KEY` | Chave secreta Django (obrigatória em produção) |
| `ALLOWED_HOSTS` | Lista separada por vírgula; hosts locais já definidos em `development` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Credenciais e conexão PostgreSQL |

> Não commite o arquivo `.env` com segredos reais.

## Migrations

```bash
python manage.py makemigrations   # se houver alterações nos models
python manage.py migrate
```

## Servidor de desenvolvimento

```bash
python manage.py runserver
```

Por padrão: `http://127.0.0.1:8000/`. O frontend de desenvolvimento esperado pelo CORS está em `http://localhost:5555`.

## Endpoints principais

Base: `http://localhost:8000`

### Usuários (`/api/v1/users/`)

| Método | Rota | Autenticação | Descrição |
|--------|------|--------------|-----------|
| POST | `/api/v1/users/register/` | Não | Cadastro (`email`, `first_name`, `password`, `password_confirm`) |
| POST | `/api/v1/users/login/` | Não | Login; retorna tokens JWT + dados do usuário |
| POST | `/api/v1/users/token/refresh/` | Não | Novo access token a partir do refresh |
| GET | `/api/v1/users/me/` | Sim | Perfil do usuário autenticado |
| GET | `/api/v1/users/search/?q=` | Sim | Busca usuários por e-mail ou nome (exclui o próprio) |

### Tarefas e categorias (`/api/v1/tasks/`)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET, POST | `/api/v1/tasks/categories/` | Lista / cria categorias do usuário |
| GET, PUT, PATCH, DELETE | `/api/v1/tasks/categories/{uuid}/` | Detalhe / atualização / exclusão |
| GET, POST | `/api/v1/tasks/` | Lista / cria tarefas (próprias e compartilhadas) |
| GET, PUT, PATCH, DELETE | `/api/v1/tasks/{uuid}/` | Detalhe; edição e exclusão apenas para o dono |
| PATCH | `/api/v1/tasks/{uuid}/toggle/` | Alterna `is_completed` (dono ou usuário com acesso compartilhado) |
| POST | `/api/v1/tasks/{uuid}/share/` | Compartilha com outro usuário (`shared_with_id`) |

**Filtros e busca (tarefas):**

- `?is_completed=true|false`
- `?priority=low|medium|high`
- `?category_id=<uuid>`
- `?search=<texto>` — busca em `title` e `description`
- `?ordering=created_at`, `due_date`, `priority`

**Paginação:** `?page=1` (tamanho de página padrão: 10).

### Exemplos rápidos (curl)

Cadastro:

```bash
curl -X POST http://localhost:8000/api/v1/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"ana@exemplo.com","first_name":"Ana","password":"SenhaSegura1","password_confirm":"SenhaSegura1"}'
```

Login (guarde o `access` da resposta):

```bash
curl -X POST http://localhost:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"ana@exemplo.com","password":"SenhaSegura1"}'
```

Listar tarefas:

```bash
curl http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Autenticação JWT

1. Obtenha `access` e `refresh` em `POST /api/v1/users/login/`.
2. Envie o access token no header: `Authorization: Bearer <access>`.
3. Access expira em **60 minutos**; refresh em **7 dias**.
4. Renovação: `POST /api/v1/users/token/refresh/` com `{"refresh": "<refresh_token>"}`.

Rotas públicas: `register`, `login`, `token/refresh`. Demais rotas exigem autenticação JWT.

## Testes

**Testes de unidade e integração (pytest):**

```bash
pytest
```

Configuração em `pytest.ini` com `DJANGO_SETTINGS_MODULE=core.settings.test`. Usa SQLite em memória para execução ágil.

**Testes e2e (Selenium):**

Requerem API e frontend no ar. Certifique-se de ter Chrome e ChromeDriver instalados.

```bash
# Sobe API e frontend
docker compose up -d

# Roda os testes e2e
pytest tests/e2e/
```

## Decisões de design

### Permissões de compartilhamento

Apenas o dono da tarefa pode compartilhá-la com outros usuários. A política de permissões é:

| Ação | Dono | Compartilhado |
|------|------|---------------|
| Visualizar | ✅ | ✅ |
| Marcar como concluída | ✅ | ✅ |
| Editar (título, descrição…) | ✅ | ❌ |
| Compartilhar com outros | ✅ | ❌ |
| Excluir | ✅ | ❌ |

Essa decisão garante que o criador da tarefa mantém controle total sobre ela, enquanto usuários convidados participam de forma colaborativa sem poder alterar dados estruturais ou propagar o acesso.

### Campo `origin` nas tarefas

A listagem de tarefas retorna um campo `origin` que indica se a tarefa pertence ao usuário autenticado (`own`) ou foi compartilhada com ele (`shared`), incluindo o e-mail do dono. Isso permite ao frontend renderizar ações condicionais (ex: ocultar botão de exclusão para tarefas compartilhadas) sem lógica extra além de checar `origin.type`.

### Outras decisões

- **JWT com resposta enriquecida:** o login retorna dados do usuário junto aos tokens, evitando uma requisição extra ao `/me/`.
- **Exceções centralizadas:** handler customizado em `core.exceptions` para respostas de erro consistentes em toda a API.
- **Settings por ambiente:** `base`, `development`, `production` e `test` — cada ambiente tem apenas o que precisa, sem condicionais espalhadas.
- **Paginação global:** `PageNumberPagination` com página de tamanho 10 aplicada por padrão a todos os endpoints de listagem.

## Possíveis melhorias futuras

- Blacklist de refresh tokens após rotação.
- Documentação interativa com OpenAPI/Swagger (drf-spectacular).
- Cobertura de testes e2e declarada em `requirements` e executada em CI.
- Endpoints de integração com serviços externos.

---

**Painel administrativo Django:** `/admin/` (usuário staff necessário).
