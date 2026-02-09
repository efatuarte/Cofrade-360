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
