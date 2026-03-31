FROM python:3.11-slim

# Evita gerar arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc

# Instala dependências Python
COPY requirements.txt .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

# Copia o projeto
COPY . .

# Porta padrão Django
EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]