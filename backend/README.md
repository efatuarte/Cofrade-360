# Backend

FastAPI backend with PostgreSQL + PostGIS

## Setup

```bash
pip install -r requirements.txt
```

## Run Database Migrations

```bash
alembic upgrade head
```

## Seed Database

```bash
python -m app.db.seed
```

## Run Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run Tests

```bash
pytest tests/
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
