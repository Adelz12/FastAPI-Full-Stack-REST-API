# FastAPI Full-Stack REST API

A production-ready REST API built with **FastAPI**, backed by **PostgreSQL** and **Redis**, containerized with **Docker**, and deployed automatically via a **Jenkins CI/CD pipeline** to a private **Harbor** registry.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI 0.111 |
| Database | PostgreSQL (async via SQLAlchemy + asyncpg) |
| Cache | Redis |
| Auth | JWT (python-jose + bcrypt) |
| Containerization | Docker + Docker Compose |
| CI/CD | Jenkins Pipeline |
| Registry | Harbor |

---

## Project Structure

```
FastAPI-Full-Stack-REST-API/
├── app/
│   ├── main.py          # App entry point, lifespan, health check
│   ├── config.py        # Settings loaded from environment variables
│   ├── database.py      # Async SQLAlchemy engine and session
│   ├── models.py        # User and Item ORM models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── auth.py          # Password hashing and JWT token creation
│   ├── deps.py          # Shared dependencies (auth, Redis, DB)
│   └── router/
│       ├── auth.py      # /auth/register and /auth/login endpoints
│       └── items.py     # /items CRUD endpoints
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive a JWT token |

### Items (Protected)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/items/` | Create a new item |
| GET | `/items/` | List all items for the authenticated user |

### Health
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check database and Redis connectivity |

---

## Getting Started (Local Development)

### 1. Clone the Repository

```bash
git clone https://github.com/Adelz12/FastAPI-Full-Stack-REST-API.git
cd FastAPI-Full-Stack-REST-API
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your local database and Redis settings:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgrespassword@localhost:5432/fastapi_dev_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

---

## Running with Docker Compose

```bash
TAG=latest docker compose up -d
```

---

## CI/CD Pipeline (Jenkins)

Every push to the `main` branch triggers the Jenkins pipeline automatically:

```
git push
    ↓
Jenkins detects change (Poll SCM every 5 minutes)
    ↓
Clone Repository
    ↓
Build Docker Image (tagged with build number)
    ↓
Push to Harbor Registry
    ↓
Deploy to Server (docker compose pull + up)
```

The pipeline is defined in the `Jenkinsfile` and uses the following credentials stored in Jenkins:
- `harbor-credentials` — Harbor robot account username and password
- `ssh-server-key` — SSH key to access the deployment server

---

## Authentication Flow

1. Register a user via `POST /auth/register`
2. Login via `POST /auth/login` to receive a JWT access token
3. Include the token in the `Authorization` header for protected endpoints:

```
Authorization: Bearer <your_token>
```

---

## Caching Strategy

The `/items/` GET endpoint uses Redis to cache results per user for **60 seconds**. When a new item is created, the cache is automatically invalidated to ensure fresh data.

---

## Environment Variables Reference

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT signing secret | — |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry duration | `30` |


---------

lets go 
