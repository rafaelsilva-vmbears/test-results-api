# syntax=docker/dockerfile:1

############################
# Etapa 1: Build de dependências
############################
FROM python:3.11-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    VENV_PATH=/opt/venv

# Instalar dependências do sistema necessárias para build
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      curl \
      ca-certificates \
      && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar arquivos de manifesto de dependências primeiro
COPY requirements.txt* /app/

# Criar virtualenv
RUN python -m venv ${VENV_PATH} && \
    ${VENV_PATH}/bin/python -m pip install --upgrade pip setuptools wheel

# Instalar dependências
# - Se existir pyproject.toml -> tenta poetry (assumindo que o projeto usa poetry)
# - Caso contrário, usa requirements.txt
RUN if [ -f "pyproject.toml" ]; then \
        ${VENV_PATH}/bin/pip install poetry && \
        # instalar dependências no venv (configurar poetry para não criar venvs)
        ${VENV_PATH}/bin/poetry config virtualenvs.create false && \
        ${VENV_PATH}/bin/poetry install --only main --no-root --no-interaction --no-ansi; \
    elif [ -f "requirements.txt" ]; then \
        ${VENV_PATH}/bin/pip install -r requirements.txt; \
    else \
        echo "Nenhum arquivo de dependência encontrado (pyproject.toml/requirements.txt)"; \
    fi

############################
# Etapa 2: Runtime (imagem final)
############################
FROM python:3.11-slim AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    VENV_PATH=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Dependências de sistema mínimas para runtime (curl para healthcheck e tini)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl \
      ca-certificates \
      tini \
      && rm -rf /var/lib/apt/lists/*

WORKDIR $APP_HOME

# Copiar virtualenv com as dependências do estágio builder
COPY --from=builder ${VENV_PATH} ${VENV_PATH}

# Copiar o código da aplicação (faça depois das dependências para melhor cache)
COPY . $APP_HOME

# Criar usuário não-root e ajustar permissões
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser && \
    mkdir -p /app/output /app/logs && \
    chown -R appuser:appgroup ${VENV_PATH} $APP_HOME /app/output /app/logs

USER appuser

EXPOSE 8000

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "run.py"]
