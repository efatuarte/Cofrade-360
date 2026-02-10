# FASE 1 — Auth + Usuario Mínimo ✅

## Checklist de Requisitos Cumplidos

### Backend
- [x] Modelo `User` con campos: id(uuid), email(unique), hashed_password, is_active, created_at
- [x] Migración Alembic `002_add_users.py` para tabla users
- [x] Security utils: password hashing (bcrypt), JWT access/refresh tokens
- [x] Endpoints implementados:
  - POST `/api/v1/auth/register`
  - POST `/api/v1/auth/login`
  - POST `/api/v1/auth/refresh`
  - POST `/api/v1/auth/logout`
  - GET `/api/v1/auth/me`
- [x] Dependencias FastAPI para `current_user` (HTTPBearer + JWT validation)
- [x] Tests pytest completos (register, login, refresh, me, errores)

### Frontend
- [x] Pantallas login/register con validación de formularios
- [x] Secure storage de tokens (flutter_secure_storage)
- [x] ApiClient con interceptor Dio (auto-refresh de tokens)
- [x] Estado global auth con Riverpod (AuthNotifier + AuthState)
- [x] Navegación condicional: no auth → LoginScreen, auth → MainScreen
- [x] Logout funcional desde perfil

---

## Archivos Creados/Modificados

### Backend
**Creados:**
- `backend/alembic/versions/002_add_users.py` - Migración tabla users
- `backend/app/core/security.py` - Password hashing + JWT utils
- `backend/app/core/deps.py` - Dependencias get_current_user
- `backend/app/api/endpoints/auth.py` - Endpoints auth
- `backend/tests/test_auth.py` - Tests completos auth
- `backend/.env.example` - Variables de entorno con SECRET_KEY

**Modificados:**
- `backend/app/models/models.py` - Añadido modelo User
- `backend/app/schemas/schemas.py` - Añadidos schemas User/Auth/Token
- `backend/app/crud/crud.py` - Añadido CRUD de usuarios
- `backend/app/api/api.py` - Registrado router auth
- `backend/app/core/config.py` - Añadidas variables SECRET_KEY, ALGORITHM, expiración tokens
- `backend/requirements.txt` - Añadidas passlib, python-jose, python-multipart

### Frontend
**Creados:**
- `frontend/lib/core/network/api_client.dart` - Cliente Dio con interceptor
- `frontend/lib/core/storage/token_storage.dart` - Secure storage tokens
- `frontend/lib/features/auth/domain/entities/user.dart` - Entidad User
- `frontend/lib/features/auth/domain/repositories/auth_repository.dart` - Interfaz repo
- `frontend/lib/features/auth/data/models/user_model.dart` - DTO User + TokenResponse
- `frontend/lib/features/auth/data/models/user_model.g.dart` - JSON serialization
- `frontend/lib/features/auth/data/repositories/auth_repository_impl.dart` - Implementación repo
- `frontend/lib/features/auth/presentation/providers/auth_provider.dart` - AuthNotifier + providers
- `frontend/lib/features/auth/presentation/screens/login_screen.dart` - Pantalla login
- `frontend/lib/features/auth/presentation/screens/register_screen.dart` - Pantalla registro

**Modificados:**
- `frontend/pubspec.yaml` - Añadida flutter_secure_storage
- `frontend/lib/main.dart` - Navegación condicional según auth
- `frontend/lib/features/perfil/presentation/perfil_screen.dart` - Botón logout + email usuario

---

## Instrucciones para Ejecutar

### 1. Backend

```bash
# Desde la raíz del proyecto
cd backend

# Instalar dependencias (si no lo has hecho)
pip install -r requirements.txt

# Levantar servicios con Docker Compose (desde raíz)
cd ..
docker compose up -d

# Esperar a que los servicios estén listos (10-15 segundos)

# Ejecutar migraciones
cd backend
alembic upgrade head

# Ejecutar tests
pytest tests/test_auth.py -v

# El API ya está corriendo en http://localhost:8000
```

### 2. Probar Endpoints (curl examples)

```bash
# 1. Registrar usuario
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Respuesta esperada:
# {"id":"...","email":"test@example.com","is_active":true,"created_at":"..."}

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Respuesta esperada:
# {"access_token":"eyJ...","refresh_token":"eyJ...","token_type":"bearer"}

# 3. Obtener info usuario (reemplaza TOKEN con el access_token del paso anterior)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer TOKEN"

# 4. Refresh token (reemplaza REFRESH_TOKEN)
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"REFRESH_TOKEN"}'

# 5. Logout
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer TOKEN"
```

### 3. Frontend

```bash
# Desde la raíz del proyecto
cd frontend

# Instalar dependencias
flutter pub get

# Generar código (JSON serialization)
flutter pub run build_runner build --delete-conflicting-outputs

# Ejecutar app (asegúrate de que el backend esté corriendo)
flutter run

# Ejecutar tests
flutter test
```

### 4. Flujo de Prueba Manual (Frontend)

1. **Primera vez**: La app muestra LoginScreen
2. **Registro**: Tap "¿No tienes cuenta? Regístrate"
   - Ingresa email válido (ej: `user@test.com`)
   - Contraseña mínimo 8 caracteres
   - Confirma contraseña
   - Tap "Registrarse"
   - Auto-login y navegación a MainScreen
3. **Navegación**: Verás los 5 tabs (Agenda, Hermandades, Itinerario, Modo Exploración, Perfil)
4. **Perfil**: Tap tab Perfil
   - Verás tu email
   - Tap icono logout (arriba derecha)
   - Vuelves a LoginScreen
5. **Login**: Ingresa credenciales y accede nuevamente

---

## Decisiones Técnicas

### Backend
- **JWT stateless**: Access token (30 min) + Refresh token (7 días). Logout es client-side (sin blacklist por ahora).
- **Bcrypt**: Hashing de passwords con passlib (rounds por defecto).
- **HTTPBearer**: Tokens en header `Authorization: Bearer <token>`.
- **Validación**: Email con EmailStr, password mínimo 8 caracteres.

### Frontend
- **flutter_secure_storage**: Tokens en keychain/keystore nativo.
- **Dio interceptor**: Auto-refresh de access token en 401, retry request.
- **Riverpod**: AuthNotifier maneja estado global, check inicial de auth al arrancar.
- **Clean Architecture**: domain/data/presentation separados, repositorio con Either<Failure, T>.

---

## Próximos Pasos

**FASE 2**: Agenda (Events) completa con filtros, paginación, validaciones y poster signed URLs.

Espera tu **"OK FASE 1"** para continuar.
