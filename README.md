# Cofrade 360 🕯️📍
Agenda cofrade + guía de hermandades + planificador inteligente de rutas “anti-bulla” para Semana Santa.

## Qué es
**Cofrade 360** es una app (Flutter) con backend API y un servicio de routing/IA que permite:
- Consultar un **calendario** de cultos, actos, ensayos, conciertos, efemérides y extraordinarias.
- Explorar fichas completas de **hermandades y cofradías** (historia, titulares, sede, multimedia, recorrido, etc.).
- Crear tu **itinerario personal** (Viernes de Dolores → Domingo de Resurrección) y recibir **rutas en tiempo real** optimizadas por contexto cofrade (carrera oficial, calles ocupadas por cortejo, bulla, calles estrechas, etc.).

---

## Stack “real” del repo (decisión tomada)
Este repo está montado como **monorepo** con:
- **Frontend:** Flutter
- **API principal:** **NestJS (TypeScript)** → usuarios, catálogo, agenda, itinerarios, media, auth, etc.
- **Motor de rutas/IA:** **FastAPI (Python)** → scoring anti-bulla + cálculo de rutas sobre grafo
- **DB:** PostgreSQL (**PostGIS recomendado** si trabajas fuerte con geodatos)
- **Cache/colas:** Redis
- **Media:** MinIO (S3 compatible) para carteles/imágenes/vídeos (metadatos en DB)
- **Docker Compose** para levantarlo todo local

> Motivo del split: NestJS es muy sólido para dominio/validaciones/estructura de producto; Python simplifica el motor de rutas y heurísticas/ML.

---

## Estructura del repositorio
```
/
  apps/
    mobile/                 # Flutter app
  services/
    api/                    # NestJS API (TypeScript)
    routing/                # FastAPI routing/IA (Python)
  infra/
    docker/
      nginx/                # (opcional) reverse proxy
  scripts/
    importers/              # ingesta/normalización de eventos y hermandades
  docker-compose.yml
  .env.example
```

---

## Requisitos
- Flutter SDK (estable)
- Node.js LTS (>= 20)
- Python (>= 3.11)
- Docker + Docker Compose

---

## Puesta en marcha (Docker)
1) Copia variables de entorno:
```bash
cp .env.example .env
```

2) Levanta infraestructura y servicios:
```bash
docker compose up -d --build
```

3) Verifica salud:
- API: http://localhost:3000/health
- Routing: http://localhost:8001/health

---

## Desarrollo local (sin Docker para código)
### Infra (solo DB/Redis/MinIO)
```bash
docker compose up -d postgres redis minio
```

### API (NestJS)
```bash
cd services/api
npm i
npm run start:dev
```

### Routing/IA (FastAPI)
```bash
cd services/routing
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### App Flutter
```bash
cd apps/mobile
flutter pub get
flutter run
```

---

## Variables de entorno (root .env)

### Base
- `ENV=dev`
- `TZ=Europe/Madrid`

### PostgreSQL
- `POSTGRES_HOST=postgres`
- `POSTGRES_PORT=5432`
- `POSTGRES_DB=cofrade360`
- `POSTGRES_USER=cofrade`
- `POSTGRES_PASSWORD=cofrade`

### Redis
- `REDIS_URL=redis://redis:6379`

### MinIO (S3)
- `S3_ENDPOINT=http://minio:9000`
- `S3_ACCESS_KEY=minioadmin`
- `S3_SECRET_KEY=minioadmin`
- `S3_BUCKET=cofrade360-media`

### API (NestJS)
- `API_PORT=3000`
- `JWT_SECRET=change_me`
- `ROUTING_SERVICE_URL=http://routing:8001`

### Routing (FastAPI)
- `ROUTING_PORT=8001`

### Mapas (opcional según proveedor)
- `MAPS_PROVIDER=google|mapbox|osrm`
- `MAPS_API_KEY=...`

---

## Contratos y endpoints (alto nivel)

### API (NestJS) - REST
- `GET /v1/events` (agenda)
- `GET /v1/events/:id`
- `GET /v1/brotherhoods` (hermandades)
- `GET /v1/brotherhoods/:id`
- `POST /v1/itineraries` (crear itinerario)
- `GET /v1/itineraries/:id`
- `POST /v1/itineraries/:id/waypoints` (puntos/horas)
- `GET /v1/media/:id` (carteles, imágenes)

### Routing/IA (FastAPI)
- `POST /route` (ruta óptima con penalizaciones)
- `POST /score` (scoring anti-bulla para depuración)
- `GET /health`

---

## Motor “anti-bulla” (resumen técnico)
El routing trabaja sobre un **grafo de calles** (nodos/intersecciones y aristas/calles) y minimiza:

`coste_total = coste_base + penalizaciones`

Penalizaciones típicas:
- **Carrera oficial:** bloqueo o coste infinito en franjas críticas.
- **Tramos ocupados por cortejo:** penalización alta (o bloqueo) en calles donde pasa la cofradía según hora y posición (cruz de guía / palio).
- **Cruces:** penalización al cruzar perpendicularmente si hay paso/público.
- **Bulla:** coste dinámico por densidad esperada (hermandad + tramo + hora + anchura de calle).

Salida: ruta + ETA + “explicación” (por qué evita ciertos tramos) para transparencia en UX.

---

## Importadores de datos
`scripts/importers/` contiene:
- normalización de eventos (agenda) y multimedia (carteles)
- normalización de fichas de hermandades
- geocodificación (si aplica) y validación

---

## Privacidad
- La ubicación solo se usa para navegación/avisos.
- Opción de **modo privacidad**: sin tracking continuo (actualización manual).
- Telemetría opcional y anonimizada.

---

## Roadmap (MVP → v1)
- [ ] Agenda (listado + filtros + detalle + carteles)
- [ ] Fichas de hermandades (mínimo viable + mapa de sede)
- [ ] Itinerario manual (timeline + mapa)
- [ ] Routing básico (sin bulla)
- [ ] Scoring anti-bulla v1 (heurístico)
- [ ] Alertas (próximo evento / cambios)
- [ ] Offline day-pack (cache por jornada)

---

## Licencia
Pendiente de definir.

---

# Propuesta de Valor (landing) + eslogan

## Eslogan
**Cofrade 360: Sevilla, paso a paso, sin bulla.**

## Hero (cabecera)
**Tu Semana Santa, perfectamente planificada.**  
Agenda completa, hermandades al detalle y rutas inteligentes en tiempo real para que llegues a lo importante sin quedarte atrapado.

## Qué problema resuelve
- “¿Qué hay hoy y dónde?” → agenda fiable con carteles y datos prácticos.  
- “Quiero saberlo todo de esta hermandad” → fichas ricas, historia y puntos clave.  
- “Estoy en la calle, ¿cómo llego sin morir en la bulla?” → routing contextual con restricciones cofrades.

## Por qué es distinta
- No es solo un mapa: **entiende la ciudad en modo Semana Santa** (carrera oficial, cortejos, cruces difíciles, calles estrechas, horas punta).
- Itinerarios **por jornada completa** (Viernes de Dolores → Domingo de Resurrección).
- Recomendaciones de visión “realistas”: dónde colocarte y cuándo moverte.

## Cómo funciona (3 pasos)
1. **Explora** la agenda y las hermandades.
2. **Diseña** tu itinerario por horas y zonas.
3. **Navega** en tiempo real con rutas optimizadas según contexto.

## CTA
- **Empieza a planificar tu Semana Santa**  
- **Crea tu itinerario en 2 minutos**

---

## FASE 6 — Operativo (Processions + StreetSegments + Restrictions)

### Migraciones
```bash
cd backend
alembic upgrade head
```

### Seed operativo
```bash
cd backend
python -m app.db.seed
```

### Endpoints clave
- `GET /api/v1/processions?date=&status=`
- `GET /api/v1/processions/{id}`
- `GET /api/v1/processions/{id}/occupations?from=&to=`
- `GET /api/v1/restrictions?from=&to=`
- `POST /api/v1/restrictions` *(admin/editor)*
- `PATCH /api/v1/restrictions/{id}` *(admin/editor)*
- `POST /api/v1/processions/occupations` *(admin/editor)*
- `PATCH /api/v1/processions/occupations/{id}` *(admin/editor)*

### Curl rápido
```bash
# Login admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@cofrade360.com","password":"test1234"}'

# Listar procesiones por fecha
curl "http://localhost:8000/api/v1/processions?date=2026-04-10T10:00:00"

# Listar restricciones activas en ventana
curl "http://localhost:8000/api/v1/restrictions?from=2026-04-10T17:00:00&to=2026-04-10T21:00:00"

# Crear restricción (admin/editor)
curl -X POST http://localhost:8000/api/v1/restrictions \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Corte puntual",
    "geom":"POLYGON((-5.99 37.39,-5.98 37.39,-5.98 37.38,-5.99 37.38,-5.99 37.39))",
    "start_datetime":"2026-04-10T18:00:00",
    "end_datetime":"2026-04-10T20:00:00",
    "reason":"corte"
  }'
```


## FASE 9 — Preferencias de Alertas

### Endpoints
- `GET /api/v1/auth/me/notifications`
- `PATCH /api/v1/auth/me/notifications`

### Ejemplo
```bash
# Obtener preferencias
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/v1/auth/me/notifications

# Desactivar alertas de restricciones
curl -X PATCH http://localhost:8000/api/v1/auth/me/notifications \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"notifications_restrictions": false}'
```


## FASE A3 — Import del dataset normalizado a DB

### Comandos
```bash
cd backend
python -m app.db.ingestion.import_hermandades_dataset
```

### Endpoint (admin/editor)
- `POST /api/v1/ingestion/hermandades/import`

### Notas
- La importación es idempotente por `name_short` (hermandad) y por `path` (media por hermandad).
- Si `MediaAsset.path` ya es URL remota (`http/https`), la API devuelve esa URL tal cual sin firmarla para facilitar estrategia “remote URL”.


## FASE A4 — Guía de actualización de dataset (operativa)

### Flujo recomendado end-to-end
```bash
# 1) Levantar entorno
cd /workspace/Cofrade-360
docker compose up -d

# 2) Migrar DB
cd backend
alembic upgrade head

# 3) Regenerar dataset normalizado desde fuentes (A2)
python -m app.db.ingestion.build_hermandades_dataset

# 4) Importar dataset a DB (A3)
python -m app.db.ingestion.import_hermandades_dataset

# 5) Verificar tests de ingestión
pytest -q backend/tests/test_ingestion.py backend/tests/test_ingestion_dataset.py backend/tests/test_ingestion_import.py
```

### Endpoints de soporte ingestión
- `GET /api/v1/ingestion/hermandades/sources`
- `POST /api/v1/ingestion/hermandades/import` *(admin/editor)*
- `GET /api/v1/provenance?entity_type=brotherhood&entity_id=<id>`

### Política de trazabilidad (provenance)
Cada registro normalizado debe incluir al menos:
- `url`
- `accessed_at`
- `fields_extracted[]`
- `status_code` (si disponible)

### Troubleshooting
- Si el entorno bloquea scraping saliente (proxy/tunnel), el builder genera igualmente `hermandades_dataset.normalized.json` con:
  - `ingestion.fetched_ok=false`
  - `ingestion.notes[]` con `fetch_error`
  - `manual_review_required:*`
- En ese caso, completar manualmente campos pendientes (`name_full`, `sede`, `schedule`, `itinerary_text`, `media`) manteniendo `provenance` antes de importar.

## FASE 11 — Data Pipeline V1 (dataset versionado + backoffice mínimo)

### Dataset versionado
- Ruta de datasets: `backend/app/db/datasets/<year>/brotherhoods.json` y `backend/app/db/datasets/<year>/processions.json`.
- Cada entrada incluye `provenance` con: `url`, `accessed_at`, `fields_extracted`, `notes`.
- Validación por Pydantic en `backend/app/db/ingest.py` (`BrotherhoodData`, `ProcessionData`).

### Ingestión CLI
```bash
# Dry-run (no persiste cambios)
python -m backend.app.db.ingest --year 2026 --dry-run

# Apply (persiste upserts)
python -m backend.app.db.ingest --year 2026 --apply
```

### Backoffice mínimo (admin)
- `GET /api/v1/admin/brotherhoods`
- `PATCH /api/v1/admin/brotherhoods/{brotherhood_id}` (sede, día, logo/media)
- `GET /api/v1/admin/processions`
- `PATCH /api/v1/admin/processions/{procession_id}` (horarios, itinerary_text, confidence)
- `GET /api/v1/admin/audit-logs`

### Auditoría y rollback
- Tabla de auditoría: `audit_logs` (actor, entidad, cambios, timestamp).
- Rollback de migración Fase 11:
```bash
cd backend
alembic downgrade -1
```

### Verificación rápida
```bash
cd backend
pytest -q
```

## FASE 12 — Routing Real V1 (grafo walkable + A* server-side)

### Modelo de datos de grafo
- `street_nodes(id, geom)`
- `street_edges(id, source_node, target_node, geom, length_m, width_estimate, highway_type, is_walkable, tags)`
- `route_restrictions(edge_id, starts_at, ends_at, reason, severity)`

### Carga de grafo
```bash
cd backend
python -m app.db.import_street_graph
```
> Este comando carga un dataset base de Sevilla centro (`backend/app/db/datasets/street_graph_sevilla.sample.json`) para desarrollo local.

### Routing
- Endpoint real: `POST /api/v1/routing/optimal`
- Soporta:
  - `origin + destination`
  - `origin + target` (compat)
- Devuelve:
  - `polyline` simplificada
  - `eta_seconds`
  - `warnings`
  - `explanation`
  - `alternatives[]`

### Caching y performance
- Cache de rutas por bucket de 10 min (`origin/destination/time_bucket/constraints`) en memoria de proceso (fallback de dev).
- Objetivo de latencia en dev para rutas medias: `< 500ms` con grafo cargado en memoria.

### Troubleshooting
- Si no hay grafo cargado, el backend entra en fallback de línea recta con warning explícito.
- Para producción, sustituir dataset sample por import OSM completo y añadir Redis cache distribuida.

## FASE 13 — Modo Calle Street-Ready (WS robusto + alertas + offline)

### Protocolo WS versionado (`/api/v1/routing/ws/mode-calle`)
- `hello` (server/client handshake)
- `location_update` (cliente -> servidor)
- `route_update` (servidor -> cliente)
- `warning` (servidor -> cliente)
- `heartbeat` (bidireccional)

### Alertas activas
- `ETA_MISS`: ETA superior al umbral de ventana (`>20 min` en baseline dev)
- `HIGH_BULLA`: bulla score alto
- `ROUTE_CUT`: corte/restricción activa en ruta

Todas las alertas y rutas publicadas por WS se persisten en `notification_events`.

### Offline degradado
- Endpoint: `GET /api/v1/routing/last?plan_id=<id>`
- Recupera la última ruta publicada por WS para continuidad cuando el socket cae.

### Frontend Modo Calle
- Banner persistente de estado: conectado/desconectado/offline + ETA + siguiente punto.
- Botón `Plan B` para recalcular priorizando ruta tranquila.
- Reconexión manual (`Reconectar`) y degradación offline con polling ligero de `routing/last`.
- Throttling de ubicación (envío cada ~5s en baseline dev).

## FASE 14 — Bulla V1 (reports + señales + agregación + anti-abuso + analítica)

### Entidades
- `crowd_reports`: reportes de usuarios (rate-limited, moderables)
- `crowd_signals`: señales agregadas por bucket temporal y geohash
- `analytics_events`: eventos estructurados con `trace_id`

### Endpoints
- `POST /api/v1/crowd/reports` (usuario autenticado)
- `GET /api/v1/crowd/signals`
- `POST /api/v1/crowd/aggregate` *(admin)*
- `PATCH /api/v1/crowd/reports/{id}` *(admin, moderación flagged/hidden)*
- `GET /api/v1/crowd/analytics` *(admin)*

### Agregación
- Bucket por 10 minutos (`aggregate_crowd_signals`)
- Confidence en función del número de reportes válidos
- Señales ocultas/moderadas no cuentan en agregación

### Integración con routing
- Se aplica `penalty_bulla` cuando `avoid_bulla=true`
- La explicación de ruta incluye detalle de penalización cuando impacta

### Frontend
- Botón de un gesto `Reportar bulla`
- `BullaMeter` visible en Modo Calle

### Verificación
```bash
cd backend
pytest -q
```
