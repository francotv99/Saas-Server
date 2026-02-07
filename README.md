# TaskFlow SaaS - Multi-Tenant Backend API

A production-oriented, multi-tenant SaaS backend API built with FastAPI, demonstrating mid-to-strong backend engineering skills.

## 🚀 Key Features

- ✅ **Multi-Tenant Architecture** - Complete data isolation per organization
- ✅ **JWT Authentication** - Secure token-based auth with role-based access control
- ✅ **Background Processing** - Async task processing with Celery and Redis
- ✅ **Clean Architecture** - Layered design (API → Services → Repositories → Models)
- ✅ **Production Ready** - Docker setup, migrations, error handling
- ✅ **Scalable Design** - Async/await throughout, horizontal scaling support

## Problem Statement

This project addresses the core challenges of building a scalable, secure, multi-tenant SaaS backend:

1. **Data Isolation**: Ensuring complete data separation between tenants (organizations)
2. **Authentication & Authorization**: Secure JWT-based auth with role-based access control
3. **Scalability**: Clean architecture that supports growth and maintainability
4. **Background Processing**: Asynchronous task processing for non-blocking operations
5. **Production Readiness**: Docker setup, migrations, and proper error handling

## Architecture Overview

### High-Level Architecture

```
┌─────────────┐
│   FastAPI   │  ← API Layer (REST endpoints)
│   (API)     │
└──────┬──────┘
       │
┌──────▼──────┐
│  Services   │  ← Business Logic Layer
└──────┬──────┘
       │
┌──────▼──────┐
│Repositories │  ← Data Access Layer (with tenant scoping)
└──────┬──────┘
       │
┌──────▼──────┐
│ PostgreSQL  │  ← Database (single DB, organization_id scoped)
└─────────────┘

┌─────────────┐
│   Celery    │  ← Background Workers
│  (Workers)  │
└──────┬──────┘
       │
┌──────▼──────┐
│    Redis    │  ← Message Broker & Cache
└─────────────┘
```

### Multi-Tenancy Strategy

**Single PostgreSQL Database with `organization_id` Scoping**

- All tenant-scoped tables include an `organization_id` column
- All queries are automatically filtered by `organization_id` at the repository level
- Users belong to exactly one organization
- JWT tokens include `organization_id` for automatic tenant resolution

**Why this approach?**
- Most common pattern in real-world SaaS applications
- Simpler to manage than schema-per-tenant
- Easier to scale horizontally
- Better for analytics and cross-tenant operations (if needed)

### Layer Responsibilities

1. **API Layer** (`app/api/`)
   - FastAPI route handlers
   - Request/response validation via Pydantic schemas
   - Dependency injection for auth, tenant scoping, RBAC

2. **Service Layer** (`app/services/`)
   - Business logic
   - Orchestrates repository calls
   - Triggers background tasks
   - Validates business rules

3. **Repository Layer** (`app/repositories/`)
   - Data access abstraction
   - Automatic tenant scoping via `BaseRepository`
   - CRUD operations with organization_id filtering

4. **Model Layer** (`app/models/`)
   - SQLAlchemy ORM models
   - Database schema definition
   - Relationships and constraints

## Key Technical Decisions

### 1. Repository Pattern
**Decision**: Use repository pattern instead of direct ORM access in services.

**Rationale**:
- Encapsulates data access logic
- Makes tenant scoping explicit and consistent
- Easier to test and mock
- Better separation of concerns

**Trade-off**: Slight overhead vs direct ORM, but improves maintainability.

### 2. Async/Await Throughout
**Decision**: Use async SQLAlchemy and async endpoints.

**Rationale**:
- Better concurrency for I/O-bound operations
- Modern Python best practice
- Scales better under load

**Trade-off**: More complex than sync, but necessary for production performance.

### 3. JWT in Token Payload
**Decision**: Include `organization_id` in JWT token.

**Rationale**:
- Eliminates need for extra DB query to resolve tenant
- Faster request processing
- Simpler dependency injection

**Trade-off**: Token invalidation requires re-login (acceptable for this use case).

### 4. Role-Based Access Control (RBAC)
**Decision**: Two roles (admin, member) with endpoint-level enforcement.

**Rationale**:
- Simple and sufficient for most SaaS needs
- Easy to extend if needed
- Clear permission model

**Trade-off**: Not as flexible as permission-based systems, but simpler to reason about.

### 5. Background Processing with Celery
**Decision**: Use Celery instead of FastAPI BackgroundTasks.

**Rationale**:
- Production-grade task queue
- Supports retries, scheduling, monitoring
- Can scale workers independently
- Better for long-running tasks

**Trade-off**: More setup complexity, but essential for production workloads.

### 6. Single Database Multi-Tenancy
**Decision**: Single PostgreSQL DB with `organization_id` columns.

**Rationale**:
- Most common SaaS pattern
- Easier operations and migrations
- Better for analytics
- Simpler backup/restore

**Trade-off**: Requires careful query scoping (handled by BaseRepository).

## Project Structure

```
saas_demo/
├── app/
│   ├── api/              # API endpoints
│   │   ├── deps.py       # FastAPI dependencies (auth, tenant, RBAC)
│   │   └── v1/           # Versioned API routes
│   ├── core/             # Core infrastructure
│   │   ├── database.py  # DB session management
│   │   ├── redis.py     # Redis connection
│   │   └── security.py  # JWT, password hashing
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── repositories/     # Data access (tenant-scoped)
│   ├── workers/          # Celery workers
│   └── utils/            # Utilities (pagination, etc.)
├── alembic/              # Database migrations
├── scripts/              # Seed data script
├── docker/               # Dockerfile
├── docker-compose.yml    # Local development setup
└── requirements.txt      # Python dependencies
```

## How to Run Locally

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (if running without Docker)

### Option 1: Docker Compose (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <repo-url>
   cd saas_demo
   cp .env.example .env
   # Edit .env if needed
   ```

2. **Start services**:
   ```bash
   docker-compose up -d db redis
   ```

3. **Run migrations**:
   ```bash
   docker-compose run --rm api alembic upgrade head
   ```

4. **Seed data**:
   ```bash
   docker-compose run --rm api python scripts/seed_data.py
   ```

5. **Start API and worker**:
   ```bash
   docker-compose up api worker
   ```

6. **Access API**:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

### Option 2: Local Development

1. **Setup virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL and Redis** (via Docker or locally):
   ```bash
   docker-compose up -d db redis
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database/redis URLs
   ```

4. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Seed data**:
   ```bash
   python scripts/seed_data.py
   ```

6. **Start API**:
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Start Celery worker** (in another terminal):
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info
   ```

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - Register new user and organization
- `POST /login` - Login and get JWT token
- `GET /me` - Get current user info

### Tasks (`/api/v1/tasks`)
- `POST /tasks` - Create task (requires auth)
- `GET /tasks` - List tasks with pagination (requires auth)
- `GET /tasks/{id}` - Get task by ID (requires auth)
- `PATCH /tasks/{id}` - Update task (requires auth)
- `DELETE /tasks/{id}` - Delete task (requires auth)

### Organizations (`/api/v1/organizations`)
- `GET /organizations/me` - Get current organization (requires auth)
- `PATCH /organizations/me` - Update organization (admin only)

## Testing Multi-Tenancy

1. **Register two organizations**:
   ```bash
   # Org 1
   curl -X POST http://localhost:8000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@acme.com","password":"admin123","organization_name":"Acme Corp","organization_slug":"acme-corp"}'
   
   # Org 2
   curl -X POST http://localhost:8000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@techstart.com","password":"admin123","organization_name":"TechStart Inc","organization_slug":"techstart-inc"}'
   ```

2. **Login and create tasks**:
   ```bash
   # Login as Org 1 admin
   TOKEN1=$(curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@acme.com","password":"admin123"}' | jq -r '.access_token')
   
   # Create task in Org 1
   curl -X POST http://localhost:8000/api/v1/tasks \
     -H "Authorization: Bearer $TOKEN1" \
     -H "Content-Type: application/json" \
     -d '{"title":"Org 1 Task","description":"This is a task"}'
   
   # Login as Org 2 admin
   TOKEN2=$(curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@techstart.com","password":"admin123"}' | jq -r '.access_token')
   
   # List tasks - should only see Org 2 tasks
   curl -X GET http://localhost:8000/api/v1/tasks \
     -H "Authorization: Bearer $TOKEN2"
   ```

## Background Processing

When a task is created, a Celery background task is triggered to send a notification (currently mocked/logged). In production, this would:

1. Send email via AWS SES / SendGrid
2. Send webhook to configured endpoints
3. Update notification queue in Redis

Check worker logs to see notifications:
```bash
docker-compose logs worker
```

## Production Considerations

### Email Provider
Currently uses mock implementation (logs to console). In production:
- Use AWS SES, SendGrid, or similar
- Configure SMTP settings in environment variables
- Implement retry logic and dead letter queues

### Security
- Change `SECRET_KEY` in production
- Use HTTPS/TLS
- Implement rate limiting
- Add request validation middleware
- Consider API key authentication for service-to-service

### Scalability
- Use connection pooling for database
- Implement Redis caching for frequently accessed data
- Consider read replicas for database
- Scale Celery workers horizontally
- Use message queue (RabbitMQ/SQS) for high-volume scenarios

### Monitoring
- Add structured logging (e.g., structlog)
- Integrate APM (e.g., Datadog, New Relic)
- Set up health checks and metrics endpoints
- Monitor Celery task execution

## Trade-offs Summary

| Decision | Pros | Cons |
|----------|------|------|
| Repository Pattern | Better testability, explicit tenant scoping | Slight overhead |
| Async/Await | Better concurrency | More complex |
| JWT with org_id | Faster requests | Token invalidation requires re-login |
| RBAC (2 roles) | Simple, clear | Less flexible than permission-based |
| Celery | Production-grade, scalable | More setup complexity |
| Single DB Multi-tenancy | Common pattern, simpler ops | Requires careful query scoping |

## License

MIT
