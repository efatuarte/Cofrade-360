# Cofrade 360 🙏

**Cofrade 360** es una aplicación móvil y backend API para planificar y seguir la Semana Santa de Sevilla. Incluye agenda de eventos, información de hermandades, cálculo de rutas inteligentes evitando cortes de calle, y modo navegación en tiempo real.

## 🏗️ Arquitectura del Monorepo

```
cofrade-360/
├── frontend/           # Flutter app (Clean Architecture + Riverpod)
├── backend/            # FastAPI + PostgreSQL + PostGIS
├── docker-compose.yml  # Servicios: API, PostGIS, Redis, MinIO
└── README.md
```

## ✨ Características

### Frontend (Flutter)
- **Clean Architecture** con separación de capas (Domain, Data, Presentation)
- **Riverpod** para gestión de estado
- **5 Tabs principales**:
  - 📅 **Agenda**: Eventos y cultos de Semana Santa
  - ⛪ **Hermandades**: Fichas de hermandades con información detallada
  - 🗺️ **Itinerario**: Planificador de rutas inteligente
  - 🚶 **Modo Calle**: Navegación en tiempo real
  - 👤 **Perfil**: Configuración y preferencias
- **Tema Claro/Oscuro** con colores de Semana Santa
- **Mock Repositories** para desarrollo sin backend

### Backend (FastAPI)
- **FastAPI** con documentación automática (Swagger/ReDoc)
- **PostgreSQL + PostGIS** para datos geoespaciales
- **SQLAlchemy ORM** con modelos para Hermandades, Eventos, Rutas
- **Alembic** para migraciones de base de datos
- **A* Routing Algorithm** para cálculo de rutas óptimas
- **API RESTful** con endpoints CRUD completos
- **Tests con pytest**

### Infraestructura (Docker)
- **PostGIS**: Base de datos espacial
- **Redis**: Cache y sesiones
- **MinIO**: Almacenamiento de imágenes (S3-compatible)
- **API**: Contenedor FastAPI con auto-reload

## 🚀 Inicio Rápido

### Requisitos Previos
- Docker & Docker Compose
- Flutter SDK (para desarrollo móvil)
- Python 3.11+ (para desarrollo backend local)

### 1. Levantar el Backend con Docker

```bash
# Levantar todos los servicios
docker-compose up -d

# Verificar que todos los servicios están corriendo
docker-compose ps

# Ver logs
docker-compose logs -f api
```

Los servicios estarán disponibles en:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

### 2. Ejecutar la App Flutter

```bash
cd frontend

# Instalar dependencias
flutter pub get

# Ejecutar en emulador o dispositivo
flutter run

# Ejecutar tests
flutter test
```

## 📊 Base de Datos

### Seed Data
La base de datos se puebla automáticamente con:
- **3 Hermandades**: Gran Poder, La Macarena, El Cachorro
- **10 Eventos**: Pregón, procesiones, cultos

### Modelos Principales

**Hermandad**
- Información básica (nombre, descripción, sede)
- Ubicación geoespacial (PostGIS)
- Fecha de fundación

**Evento**
- Título, descripción, fecha/hora
- Ubicación y coordenadas
- Relación con hermandad

**Ruta**
- Geometría de línea (LINESTRING)
- Distancia y duración
- Nodos y aristas para grafo de navegación

## 🧪 Testing

### Backend Tests
```bash
cd backend
pip install -r requirements.txt
pytest tests/
```

Tests incluidos:
- ✅ API endpoints (health, hermandades, eventos, routing)
- ✅ Algoritmo A* con grafo mock
- ✅ Cálculo de distancias Haversine

### Frontend Tests
```bash
cd frontend
flutter test
```

Tests incluidos:
- ✅ Smoke test de la aplicación
- ✅ Navegación entre tabs
- ✅ Carga de pantallas principales

## 🗺️ Routing con A*

El sistema de enrutamiento usa el algoritmo **A*** sobre un grafo que representa las calles de Sevilla.

**Características**:
- Cálculo de ruta óptima entre dos puntos
- Evita calles bloqueadas por procesiones
- Distancias reales usando fórmula Haversine
- Preparado para integrar grafo real de OpenStreetMap

**Endpoint**: `POST /api/v1/routing/optimal`

```json
{
  "origen": [37.3862, -5.9926],
  "destino": [37.4008, -5.9900],
  "evitar_procesiones": true
}
```

## 🛠️ Desarrollo

### Estructura del Código

**Frontend (Clean Architecture)**
```
lib/
├── core/               # Theme, utils, errors
├── features/           # Features con Domain/Data/Presentation
│   ├── agenda/
│   ├── hermandades/
│   ├── itinerario/
│   ├── modo_calle/
│   └── perfil/
└── shared/             # Widgets y componentes compartidos
```

**Backend**
```
app/
├── api/                # API routes y endpoints
├── core/               # Config, routing algorithm
├── crud/               # Database operations
├── db/                 # Database session y seed
├── models/             # SQLAlchemy models
└── schemas/            # Pydantic schemas
```

### Comandos Útiles

**Docker**
```bash
# Reconstruir servicios
docker-compose build

# Ver logs de un servicio específico
docker-compose logs -f api

# Parar servicios
docker-compose down

# Parar y eliminar volúmenes
docker-compose down -v
```

**Backend**
```bash
# Crear nueva migración
alembic revision --autogenerate -m "description"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1
```

**Frontend**
```bash
# Generar código (Riverpod, JSON)
flutter pub run build_runner build --delete-conflicting-outputs

# Analizar código
flutter analyze

# Formatear código
flutter format lib/
```

## 📝 API Endpoints

### Hermandades
- `GET /api/v1/hermandades` - Listar hermandades
- `GET /api/v1/hermandades/{id}` - Obtener hermandad por ID
- `POST /api/v1/hermandades` - Crear hermandad

### Eventos
- `GET /api/v1/eventos` - Listar eventos
- `GET /api/v1/eventos/{id}` - Obtener evento por ID
- `POST /api/v1/eventos` - Crear evento

### Routing
- `POST /api/v1/routing/optimal` - Calcular ruta óptima

## 🔮 Próximos Pasos

- [ ] Integrar grafo real de OpenStreetMap
- [ ] Notificaciones push para eventos cercanos
- [ ] Chat/foro de cofrades
- [ ] Galería de fotos por hermandad
- [ ] Modo offline con sincronización
- [ ] Compartir itinerarios entre usuarios

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles

## 👥 Contribuir

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

**Desarrollado con ❤️ para la Semana Santa de Sevilla**
