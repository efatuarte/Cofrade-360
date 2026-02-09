# Cofrade-360 Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Flutter)                        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Presentation Layer (Widgets)                 │  │
│  │  ┌──────┬───────────┬───────────┬────────────┬─────────┐ │  │
│  │  │Agenda│Hermandades│Itinerario │Modo Calle  │ Perfil  │ │  │
│  │  └──────┴───────────┴───────────┴────────────┴─────────┘ │  │
│  │                      ↕ Riverpod State                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Domain Layer                            │  │
│  │  [Entities] → [Use Cases] → [Repository Interfaces]      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Data Layer                              │  │
│  │  [Repository Impl] → [Data Sources: API / Mock]          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                │ HTTP/REST
                                │
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   API Layer                               │  │
│  │  [Endpoints] → [Schemas] → [Dependencies]                │  │
│  │  /hermandades, /eventos, /routing/optimal                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Business Logic                           │  │
│  │  [CRUD Operations] → [A* Routing Algorithm]              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Database Layer                           │  │
│  │  [SQLAlchemy Models] → [Alembic Migrations]              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└───┬──────────────────┬──────────────────┬─────────────────────────┘
    │                  │                  │
    ↓                  ↓                  ↓
┌─────────┐      ┌─────────┐      ┌─────────┐
│PostGIS  │      │ Redis   │      │ MinIO   │
│PostgreSQL│     │ Cache   │      │ S3      │
│Spatial DB│     │Sessions │      │ Storage │
└─────────┘      └─────────┘      └─────────┘
```

## Clean Architecture (Flutter)

### Presentation → Domain → Data

**Key Principle**: Dependencies point inward. Domain has no dependencies.

## API Endpoints

- GET `/` - Root
- GET `/health` - Health check
- GET `/api/v1/hermandades` - List brotherhoods
- GET `/api/v1/eventos` - List events
- POST `/api/v1/routing/optimal` - Calculate route

## A* Routing Algorithm

Uses Haversine distance heuristic with graph of Seville landmarks.

---

**Last Updated**: 2026-02-09
