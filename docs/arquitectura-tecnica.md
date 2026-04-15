# Arquitectura técnica propuesta (MVP)

## 1. Stack sugerido

- **Frontend:** Next.js (App Router) + TypeScript + Tailwind.
- **Backend/API:** Next.js API routes o servicio Node.js con Fastify.
- **Base de datos:** PostgreSQL.
- **Cache/colas:** Redis (caching de tendencias + rate limiting).
- **Auth:** JWT con refresh token o proveedor (Auth.js/Clerk).
- **Hosting:** Vercel (frontend) + Neon/Supabase (Postgres) + Upstash/Redis.

## 2. Modelo de datos (relacional)

### Tabla `users`

- `id` (uuid, pk)
- `email` (unique)
- `password_hash`
- `created_at`
- `last_poll_created_at`
- `status` (active, suspended)

### Tabla `polls`

- `id` (uuid, pk)
- `author_id` (fk -> users)
- `question`
- `option_a`
- `option_b`
- `created_at`
- `status` (active, hidden, deleted)
- `reports_count`

### Tabla `votes`

- `id` (uuid, pk)
- `poll_id` (fk -> polls)
- `user_id` (fk -> users)
- `choice` (A|B)
- `created_at`
- Restricción única: (`poll_id`, `user_id`)

### Tabla `poll_reports`

- `id` (uuid, pk)
- `poll_id` (fk -> polls)
- `user_id` (fk -> users)
- `reason`
- `created_at`

### Tabla `daily_featured_poll`

- `date` (pk)
- `poll_id` (fk -> polls)

## 3. Endpoints API (ejemplo)

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/polls`
- `GET /api/polls/feed?cursor=...`
- `POST /api/polls/:id/vote`
- `GET /api/polls/:id/results`
- `POST /api/polls/:id/report`
- `GET /api/polls/trending`

## 4. Lógica crítica

### 4.1 Límite de creación de encuestas

Al crear encuesta:

1. Leer `last_poll_created_at` del usuario.
2. Comparar con `now - cooldown_days`.
3. Si no cumple, devolver `429` con fecha de próximo desbloqueo.
4. Si cumple, crear encuesta y actualizar `last_poll_created_at`.

### 4.2 Votación atómica

- Transacción SQL:
  - Insertar voto si no existe.
  - Si existe conflicto único, devolver error "ya votaste".
- Resultados calculados por agregación SQL + caché breve (5–15s).

### 4.3 Tendencias

Score sugerido:

`trend_score = votos_24h * 0.7 + votos_1h * 1.3 + ratio_crecimiento * 1.0`

Recalcular cada pocos minutos con job programado.

## 5. Escalabilidad

- Indexar columnas clave (`created_at`, `poll_id`, `author_id`).
- Cursor pagination para feed (no offset).
- Cache Redis para feed de tendencia.
- Separar servicio de jobs (cron/queue) al crecer.

## 6. Seguridad y abuso

- Hash de contraseña (Argon2/Bcrypt).
- Rate limiting por IP + usuario.
- Validación de input y sanitización.
- CSRF en formularios con sesión.
- Auditoría mínima de acciones sensibles.

## 7. Analítica

Eventos mínimos:

- `poll_viewed`
- `poll_voted`
- `poll_created`
- `ad_impression`
- `session_started`

Herramientas: PostHog, Plausible o GA4.
