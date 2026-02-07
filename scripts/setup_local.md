# Setup Local (Sin Docker)

## Opción 1: PostgreSQL y Redis locales

### Windows (usando Chocolatey o instaladores)

1. **PostgreSQL**:
   - Descarga desde: https://www.postgresql.org/download/windows/
   - O usa Chocolatey: `choco install postgresql15`
   - Crea la base de datos:
     ```sql
     CREATE DATABASE taskflow_db;
     ```

2. **Redis**:
   - Descarga desde: https://github.com/microsoftarchive/redis/releases
   - O usa WSL2 con Redis
   - O usa Docker solo para Redis: `docker run -d -p 6379:6379 redis:7-alpine`

### Configurar .env

Tu `.env` ya está configurado para localhost:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/taskflow_db
REDIS_URL=redis://localhost:6379/0
```

### Ejecutar

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
alembic upgrade head

# Seed data
python scripts/seed_data.py

# Iniciar API
uvicorn app.main:app --reload

# En otra terminal, iniciar Celery worker
celery -A app.workers.celery_app worker --loglevel=info
```

## Opción 2: Solo Redis en Docker

Si tienes PostgreSQL local pero quieres Redis en Docker:

```bash
# Solo iniciar Redis
docker run -d -p 6379:6379 --name taskflow_redis redis:7-alpine

# Luego ejecutar migraciones y API localmente
alembic upgrade head
python scripts/seed_data.py
uvicorn app.main:app --reload
```
