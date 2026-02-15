# FASE 0 — Auditoría rápida (sin tocar funcionalidad)

## Estado actual detectado

### Backend
- **Modelos**: existen `User`, `Location`, `Hermandad`, `Evento` y modelos de routing (`Ruta`, `Nodo`, `Arista`).
- **Schemas**: hay enums y validación para eventos (fechas y coherencia de precio/gratuidad), paginación genérica y schemas de auth.
- **CRUD**: separación por funciones en `app/crud/crud.py` con operaciones de usuario, location, hermandades y eventos.
- **Endpoints**:
  - Auth: `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me`.
  - Agenda: `/events` (paginación + filtros), `/events/{id}`, `POST/PATCH /events`, `/events/{id}/poster` (placeholder signed URL).
  - Hermandades: listado básico, detalle y creación.
  - Routing: `/routing/optimal` (A* mock en memoria).
- **Errores API**: hay handlers globales con formato uniforme `{detail, code, trace_id}` para HTTP, validación y errores 500.
- **Migrations/Alembic**: existen revisiones 001, 002, 003 (PostGIS + tablas base + users + expansión de eventos/location).
- **Seed**: incluye usuario de prueba, locations, 3 hermandades y 10 eventos realistas.
- **Infra**: `docker-compose` levanta PostGIS, Redis, MinIO y API; API corre migraciones y seed al inicio.

### Frontend (Flutter)
- **Arquitectura base**: estructura por `features/*/{data,domain,presentation}` en agenda/hermandades/auth; Riverpod en uso.
- **Auth**: login/register implementados, `AuthNotifier`, secure storage y cliente Dio con interceptor + refresh token.
- **Navegación inicial**: gate por estado auth (`LoginScreen` vs `MainScreen`) ya implementado.
- **Agenda**: pantalla funcional con lista, filtros, búsqueda, estados loading/error/data y detalle.
- **Hermandades**: listado funcional con carga API y estado async.
- **Itinerario y Modo Calle**: pantallas aún de tipo placeholder (sin vertical funcional completo).

## Gaps respecto al objetivo final por fases

### Ya cubierto de forma parcial/fuerte
- FASE 1 (auth) **muy adelantada** en backend y frontend.
- FASE 2 (agenda) **parcial-alta**: filtros/paginación/CRUD básicos y UI funcional.

### Pendiente o incompleto
- **FASE 2**: `GET /events/{id}/poster` aún placeholder, falta signed URL real MinIO.
- **FASE 3**: no existen aún `MediaAsset` ni endpoints de upload signed PUT/GET; hermandades sin filtro/paginación avanzada ni media gallery real.
- **FASE 4**: faltan modelos/endpoints de `UserPlan`/`PlanItem`, detección de solapes y optimización.
- **FASE 5**: falta WebSocket `/ws/mode-calle`, contrato nuevo de routing (`origin/datetime/target/constraints`) y `bulla_score` con explicación.
- **Frontend FASE 4/5**: itinerario y modo calle requieren implementación completa con API/WS.

## Riesgos técnicos (3) y mitigación

1. **PostGIS + migraciones en limpio (riesgo de incompatibilidad en CI/local)**
   - Riesgo: columnas `Geometry` + operaciones `CREATE EXTENSION` pueden fallar si no se usa imagen compatible o permisos limitados.
   - Mitigación:
     - Mantener `postgis/postgis` como DB de referencia en dev/CI.
     - Añadir smoke test de `alembic upgrade head` en pipeline.
     - Evitar SQL espacial no necesario para MVP y encapsular en utilidades.

2. **Signed URLs MinIO (riesgo de expiración, CORS y acceso desde móvil)**
   - Riesgo: URL firmada inválida por desfase de reloj, endpoint interno (`minio:9000`) no resoluble desde cliente, o CORS de bucket.
   - Mitigación:
     - Generar URL con host público configurable (`MINIO_PUBLIC_ENDPOINT`).
     - Normalizar expiraciones y validar clock skew.
     - Documentar y aplicar política CORS de bucket `media`.

3. **WebSocket Modo Calle (riesgo de reconexión/fugas y recalculado excesivo)**
   - Riesgo: clientes móviles con red inestable, reconexiones constantes y reroute demasiado frecuente (coste/carga).
   - Mitigación:
     - Protocolo con heartbeat + `throttle` por tiempo/distancia.
     - Reglas de reroute por umbral (cambio ETA significativo o warning severo).
     - Separar capa `routing engine` para poder sustituir mock A* por grafo real sin romper contrato API.
