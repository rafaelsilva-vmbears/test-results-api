# Test Results API

A high-performance API developed with **FastAPI** to register, store, and query automated test execution results. It provides a robust backend for collecting metrics, querying history, and integrating with visualization dashboards like Grafana or Power BI.

## 🚀 Features

- **Store & Query**: Seamlessly register and retrieve test execution data.
- **Analytics**: Aggregated metrics (pass rate, failure trends) by project and period.
- **Security**: Global authentication via `X-API-Key`.
- **Standards**: Clean Architecture, Pydantic V2 validation, and OpenAPI (Swagger) integration.
- **Automation**: Ready-to-use CI/CD components and XML report processing.

---

## 🏛️ Architecture

This project strictly adheres to **Clean Architecture** principles, ensuring scalability and maintainability:

```text
test-results-api/
├── app/
│   ├── api/                # Presentation Layer (FastAPI routes, schemas, handlers)
│   ├── application/        # Application Layer (Business rules orchestration/Use Cases)
│   ├── domain/             # Domain Layer (Core entities, interfaces, and logic)
│   ├── infrastructure/     # Infrastructure Layer (DB adapters, repositories, logging)
│   ├── bootstrap/          # App initialization (Lifespan, factory)
│   └── utils/              # Cross-cutting utilities
├── tests/                  # Pyramid Testing Suite (Unit, Integration, Component)
└── .github/                # CI/CD Workflows
```

---

## 🛡️ Authentication & Authorization

All endpoints are protected by a mandatory `X-API-Key` header. The system supports multi-tenant API Keys with granular permissions.

- **Header**: `X-API-Key: <YOUR_API_KEY>`
- **Permissions**:
    - `READ`: Allows access to `GET` endpoints (e.g., listing projects, viewing results).
    - `WRITE`: Allows access to `POST`/`DELETE` endpoints (e.g., uploading XMLs, creating executions).
    - `ADMIN`: Full access (reserved for special cases).

### Admin & Key Management

Administrative endpoints are protected by a **Master Key**.

- **Master Key Configuration**: Set `MASTER_KEY` in your `.env`.
- **Endpoints** (`/admin/api-keys`):
    - `POST /`: Create a new key for a team (requires `team_name` and `permissions`).
    - `GET /`: List all active keys.
    - `PUT /{key}`: Update permissions for an existing key.
    - `DELETE /{key}`: Revoke a key.

> **Note**: For backward compatibility, the legacy `API_KEY` env var acts as a Super Admin key if set.

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.12+
- MongoDB (Local or Atlas)

### Local Environment
1. **Clone & Enter**:
   ```bash
   git clone <repository-url>
   cd test-results-api
   ```
2. **Setup Venv**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```
3. **Install**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment**:
   ```bash
   cp example.env .env
   # Edit .env with your MONGO_URI and MASTER_KEY
   ```

---

## 🐳 Docker Deployment

The project includes a multi-profile `docker-compose.yml` for flexibility.

### 1. Production/Cloud (MongoDB Atlas)
Run the API connected to a remote MongoDB instance:
```bash
docker compose up -d api
```

### 2. Full Local Development
Run the API, MongoDB, and Mongo Express locally:
```bash
docker compose --profile local up -d
```
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Database UI**: [http://localhost:8081](http://localhost:8081)

---

## ⚡ Local Development (sem MongoDB)

Para desenvolvimento local e demos de QA, a API suporta um banco **in-memory** via [`mongomock`](https://github.com/mongomock/mongomock) — sem necessidade de instalar MongoDB, Docker ou Atlas.

### Ativação

No `.env`, defina:

```env
USE_MONGOMOCK=true
```

> Se `MONGO_URI` estiver vazio, o modo in-memory é ativado automaticamente.

### Fluxo de Demo QA

```bash
# 1. Suba a API (banco in-memory vazio)
python run.py

# 2. Em outro terminal, carregue os dados de exemplo
python seed_data.py --project gdcr --env uat

# 3. Explore os dados no Swagger
# http://localhost:8000/docs

# 4. Para resetar o banco: Ctrl+C -> python run.py
```

### Opções do `seed_data.py`

| Comando | Descrição |
|---|---|
| `python seed_data.py` | Carrega `data/*.xml` (project/env extraídos do nome do arquivo) |
| `python seed_data.py --project gdcr --env uat` | Força project e environment para todos os arquivos |
| `python seed_data.py --dir outra-pasta` | Usa outra pasta de XMLs |
| `python seed_data.py --clean` | Exibe instrução de reset (reiniciar a API limpa o banco in-memory) |

> **Nota**: O banco in-memory não persiste entre execuções. Todos os dados são perdidos ao reiniciar a API — ideal para demos e testes exploratórios.

---

## 🔌 SDK & Integration

To facilitate integration with CI/CD pipelines (Jenkins, GitHub Actions, GitLab), we provide a ready-to-use **Python SDK**.

### Python CLI Script
Located in [`sdk/python/`](sdk/python/), the `submit_results.py` script allows you to submit XML test results with a simple command:

```bash
python sdk/python/submit_results.py \
  --file results.xml \
  --project "MyProject" \
  --environment "Staging" \
  --url "http://api.yourservice.com" \
  --key "YOUR_API_KEY"
```

👉 **[See full SDK Documentation](sdk/python/README.md)** for detailed CI/CD examples.

---


## 🧪 Testing Strategy

We follow the **Test Pyramid** to ensure maximum reliability with high execution speed.

### Running Pytest
```bash
# Full Suite
pytest

# By Layer
pytest tests/unit         # Fast business logic verification
pytest tests/integration  # Database repository interactions (via mongomock)
pytest tests/component    # End-to-end API request/response flow
```

### CI/CD Workflow
The GitHub Actions pipeline (`ci.yml`) automatically:
1. Runs **Unit Tests** (must pass 80% coverage).
2. Runs **Integration Tests**.
3. Runs **Component Tests**.
4. Posts a result summary as a **Pull Request Comment**.

---

## 📄 Documentation (Swagger)

Interactive documentation is enabled via FastAPI's Swagger UI.
- **Docs Path**: `/docs`
- **Security**: Click **"Authorize"** to insert your `X-API-Key` and test endpoints directly.

---

## 👥 Authors

- **Tito Santos** - Lead Developer & Technical Owner
- **Rafael Silva** - Co-Developer & Agent Contributor
