# IncidenciaIQ

https://incidenciaiq.onrender.com/

**Monitoreo inteligente de incidencias operativas, todo en español.**

Plataforma web SaaS para centralizar, registrar, clasificar y analizar incidencias de TI u operaciones. Combina una API REST (FastAPI), base de datos PostgreSQL y un agente de IA que clasifica cada incidencia automáticamente, genera perspectivas, responde preguntas operativas y además **mide su propia precisión** con datos reales.

---

## Tabla de contenidos

1. [Características](#características)
2. [Stack tecnológico](#stack-tecnológico)
3. [Arquitectura](#arquitectura)
4. [Modelo de datos](#modelo-de-datos)
5. [Estructura del proyecto](#estructura-del-proyecto)
6. [Puesta en marcha local](#puesta-en-marcha-local)
7. [Variables de entorno](#variables-de-entorno)
8. [El subsistema de IA](#el-subsistema-de-ia)
9. [Documentación de la API](#documentación-de-la-api)
10. [Tests](#tests)
11. [Despliegue en Render + Neon](#despliegue-en-render--neon)
12. [Docker](#docker)
13. [Solución de problemas](#solución-de-problemas)
14. [Roadmap](#roadmap)
15. [Licencia](#licencia)

---

## Características

- **Registro de incidencias** con categoría, prioridad y estado (catálogos sembrados: Acceso, Pagos, Sistema, Red, Otros).
- **Clasificación IA automática** en el mismo POST de creación: sugiere categoría, prioridad, resumen, recomendación, confianza y **justificación trazable**.
- **Explicabilidad real**: cada sugerencia registra su `fuente` (`openai`, `heuristic`, `case`, `openai_case`, `heuristic_case`) y referencia un **caso histórico** con su **índice de similitud**.
- **AI Help**: asistente en lenguaje natural sobre datos reales de la BD, con delimitación temporal precisa (diferenciación entre actividad de la semana actual e histórico acumulado) y respaldo determinista por reglas si no hay API key.
- **Perspectivas automáticas**: detectan incrementos, caídas y actividad anómala por categoría comparando el período real contra el período anterior.
- **Evaluación del clasificador**: precisión, cobertura, aciertos/errores globales y desglose por fuente y por categoría, calculados solo con datos reales.
- **Analítica completa**: KPIs con comparación vs período anterior, desglose por categoría, tendencia (diaria/horaria) y estadísticas de tiempo de resolución (promedio, mediana, P95, por categoría/prioridad).
- **Historial de auditoría**: cada cambio (estado, prioridad, categoría, notas, confirmación) queda registrado con autor, fecha y valores anterior/nuevo.
- **Cierre automático**: al pasar a "Cerrada" se calcula `tiempo_resolucion_minutos` y `resuelto_en` automáticamente.
- **UI en español** construida con React + Tailwind: Dashboard, Incidencias, Detalle, Analítica y AI Help.
- **Sin dependencias pesadas de ML**: el índice TF-IDF está implementado en Python puro.

---

## Stack tecnológico

| Capa | Tecnología |
| --- | --- |
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2.0 (ORM) · Pydantic v2 (settings y schemas) |
| Base de datos | PostgreSQL 15 (psycopg v3) |
| IA | OpenAI API (`gpt-4o-mini`) + reglas deterministas + TF-IDF/coseno en Python puro |
| Frontend | React 18 · Vite 6 · Tailwind CSS · Recharts · lucide-react · react-router-dom |
| Cliente HTTP | Axios |
| Infraestructura | Docker · Multi-stage Dockerfile · Render (Web Service) · Neon (Postgres) |
| Testing | pytest (FastAPI TestClient) |

---

## Arquitectura

```mermaid
flowchart LR
    U[Navegador / Usuario] -->|HTTPS| R[Render Web Service]
    R -->|sirve SPA: dist/ + fallback| F[Frontend React]
    R -->|/api/*| B[FastAPI · app/main.py]
    R -->|/api/health, /docs| B
    B --> S1[servicio_incidencias]
    B --> S2[servicio_analitica]
    B --> S3[servicio_ia]
    S3 --> S4[servicio_casos: TF-IDF + coseno]
    S3 --> S5[servicio_evaluacion]
    S1 & S2 & S3 -->|SQLAlchemy| PG[(Postgres · Neon)]
    S3 -->|chat.completions| LLM[OpenAI gpt-4o-mini]
    LLM -. no hay API key .-> H[Heurística por palabras clave]
```

**Notas de la arquitectura:**

- En producción la UI y la API viven en el **mismo servicio** (un solo Web Service en Render): FastAPI sirve el frontend compilado (`dist/`) mediante `StaticFiles` + fallback SPA (`main.py:_montar_frontend`). Esto elimina problemas de CORS y reduce coste.
- En desarrollo local el frontend corre en Vite (`:5173`) con proxy `/api` → `:8000` (`frontend/vite.config.js`).
- El índice TF-IDF se construye **en memoria por request** sobre incidencias reales (cerradas o con análisis confirmado); no hay base vectorial.

---

## Modelo de datos

> Nota: los atributos en el código están en español; los nombres reales de columnas en la base de datos quedan en inglés explícito mediante `mapped_column("columna_original")`, para mantener compatibilidad con el esquema original.

```mermaid
erDiagram
    CATEGORIES ||--o{ INCIDENTS : "categoria"
    PRIORITIES ||--o{ INCIDENTS : "prioridad"
    STATES ||--o{ INCIDENTS : "estado"
    INCIDENTS ||--o| AI_ANALYSES : "analisis (1..0)"
    AI_ANALYSES }o--|| CATEGORIES : "categoria_sugerida"
    AI_ANALYSES }o--|| PRIORITIES : "prioridad_sugerida"
    INCIDENTS ||--o{ INCIDENT_HISTORY : "historial"
    AI_ANALYSES }o--o| INCIDENTS : "incidencia_referencia"

    CATEGORIES {
        int id PK
        text name
        text description
        text color
        text icon
    }
    PRIORITIES {
        int id PK
        text name
        int level
        text color
        text icon
    }
    STATES {
        int id PK
        text name
        text description
        text color
    }
    INCIDENTS {
        int id PK
        int category_id FK
        int priority_id FK
        int state_id FK
        text title
        text description
        timestamp created_at
        timestamp updated_at
        text created_by
        text notes
        int resolution_time_minutes
        timestamp resolved_at
    }
    AI_ANALYSES {
        int id PK
        int incident_id FK "unique"
        int suggested_category_id FK
        int suggested_priority_id FK
        text summary
        text recommendation
        float confidence
        boolean is_confirmed
        text source
        text rationale
        int reference_incident_id FK
        float similarity_score
        timestamp created_at
    }
    INCIDENT_HISTORY {
        int id PK
        int incident_id FK
        text action
        text previous_value
        text new_value
        text changed_by
        timestamp created_at
    }
```

---

## Estructura del proyecto

```
IncidentIQ/
├── Dockerfile                 # Multi-stage: build frontend + backend (un solo servicio)
├── README.md
├── .gitignore
├── backend/
│   ├── Dockerfile             # Imagen del backend sola (dev / docker-compose)
│   ├── docker-compose.yml     # Postgres + backend para desarrollo local
│   ├── requirements.txt       # Dependencias fijadas (pinned)
│   ├── .env.example           # Plantilla de variables de entorno
│   ├── tests/                 # pytest (unitarios y de integración)
│   │   ├── __init__.py
│   │   ├── test_ia.py         # pruebas de heurística y asistente
│   │   └── test_api_completo.py # suite integral de todos los endpoints y SPA
│   └── app/
│       ├── main.py            # App FastAPI, CORS, health, seed, montaje del frontend
│       ├── configuracion.py   # Settings desde env (pydantic-settings)
│       ├── base_de_datos.py   # Engine SQLAlchemy, SessionLocal, Base
│       ├── sembrar.py         # Catálogos + incidencias demo (idempotente)
│       ├── models/            # ORM: categoria, prioridad, estado, incidencia, analisis_ia, historial_incidencia
│       ├── schemas/           # Pydantic: incidencia, analitica, ia, error
│       ├── routers/           # incidencias, analitica, ia
│       ├── services/          # servicio_incidencias, servicio_analitica, servicio_ia, servicio_casos, servicio_evaluacion
│       ├── prompts/           # clasificacion, asistente, analisis (prompts para OpenAI)
│       └── utils/             # errores (HTTPExceptions), logger
└── frontend/
    ├── package.json
    ├── vite.config.js         # dev server :5173, proxy /api -> :8000
    └── src/
        ├── main.jsx            # Punto de entrada React
        ├── App.jsx             # Rutas (react-router-dom)
        ├── pages/              # Panel, Incidencias, DetalleIncidencia, Analitica, AyudaIA, NotFound
        ├── components/         # Layout, Panel, Incidencias, DetalleIncidencia, Analitica, AI, Common
        ├── services/           # api (axios), servicioIncidencias, servicioAnalitica, servicioIA
        ├── hooks/              # useIncidencias, useAnalitica, useIA
        ├── constants/          # rutas, categorias, prioridades, estados
        ├── utils/              # formatters, helpers, validators
        └── context/            # contextoNotificacion (toasts)
```

---

## Puesta en marcha local

### Requisitos

- Python 3.12+
- Node.js 20+
- Docker (para PostgreSQL) — o una instancia Postgres accesible

### 1. Base de datos

```bash
cd backend
docker compose up -d db        # Postgres 15 en 127.0.0.1:5433, db: incident_iq
```

> Nota: usa credenciales locales `postgres:postgres`. El esquema y los datos de referencia se crean solos al arrancar el backend (`create_all` + `sembrar`).

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows  ·  source .venv/bin/activate (Linux/macOS)
pip install -r requirements.txt
cp .env.example .env          # ajusta DATABASE_URL y OPENAI_API_KEY si quieres
uvicorn app.main:app --reload --port 8000
```

Verificación:

- Swagger / API docs → http://localhost:8000/docs
- Health → http://localhost:8000/api/health

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Verificación:

- App → http://localhost:5173 (el proxy redirige `/api` a `:8000`)
- Build de producción: `npm run build` (genera `frontend/dist/`)

---

## Variables de entorno

Todas son opcionales salvo `DATABASE_URL` (en producción). Fuente: `app/configuracion.py`.

| Variable | Default | Descripción |
| --- | --- | --- |
| `APP_NAME` | `IncidenciaIQ` | Nombre de la app (health check) |
| `APP_VERSION` | `1.2.0` | Versión expuesta en `/api/health` |
| `ENVIRONMENT` | `development` | Modo del entorno (`production` recomendado en despliegue) |
| `API_DEBUG` | `true` | Debug de la app |
| `API_HOST` | `0.0.0.0` | Host del servidor |
| `API_PORT` | `8000` | Puerto del servidor |
| `API_CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Orígenes permitidos (CSV). En Render puedes dejarlo vacío (UI y API same-origin). |
| `DATABASE_URL` | local Docker `postgresql+psycopg://postgres:postgres@127.0.0.1:5433/incident_iq` | Cadena de conexión. **Acepta `postgresql://` sin driver**: se normaliza a `postgresql+psycopg://` automáticamente. |
| `DATABASE_POOL_SIZE` | `10` | Pool de conexiones |
| `DATABASE_MAX_OVERFLOW` | `20` | Overflow del pool |
| `OPENAI_API_KEY` | vacío | Key de OpenAI. **Vacío = clasificador heurístico determinista** (todo sigue funcionando, sin coste). |
| `OPENAI_MODEL` | `gpt-4o-mini` | Modelo de chat |
| `OPENAI_MAX_TOKENS` | `1000` | Máximo de tokens por respuesta |
| `OPENAI_TEMPERATURE` | `0.7` | Temperatura de muestreo |
| `OPENAI_TIMEOUT_SECONDS` | `30.0` | Timeout de la llamada a la API |
| `LOG_LEVEL` | `INFO` | Nivel de logging |

---

## El subsistema de IA

### Cómo se clasifica una incidencia (creación)

1. **Recomendación basada en casos** (`servicio_casos.py`): se construye un índice **TF-IDF** (propio, sin librerías) sobre incidencias **cerradas** + incidencias cuyo análisis fue **confirmado** por un analista. Se busca el caso más similar por **similitud de coseno** con umbral `0.30`.
2. **LLM (si hay API key)** (`servicio_ia._llamar_llm`): se genera un prompt con el título y la descripción y se pide un JSON estructurado.
3. Se decide la **fuente de la verdad**:

| Condición | `fuente` | Confianza |
| --- | --- | --- |
| LLM válido + caso histórico | `openai_case` | `0.6·conf_llm + 0.4·similitud` |
| LLM válido sin caso | `openai` | la del modelo |
| Sin LLM, con caso histórico | `heuristic_case` | `0.6·conf_reglas + 0.4·similitud` |
| Sin LLM, heurística "Otros", con caso | `case` | `min(similitud + 0.25, 0.9)` |
| Sin LLM (solo reglas) | `heuristic` | reglas por palabras clave (0.55–0.97) |

4. Se persiste `ai_analyses` con `fuente`, `justificacion`, `incidencia_referencia_id` e `indice_similitud`, y se devuelve la incidencia ya clasificada.

> La clasificación es **best-effort**: nunca impide la creación de la incidencia (si falla la IA, la incidencia queda igualmente guardada sin análisis).

### Decisiones de negocio

- `SLA_TARGET_MINUTES = 480` — el SLA se mide contra 8 horas (`servicio_analitica.py:11`).
- El historial registra `Creada`, `Cambio de estado`, `Cambio de prioridad`, `Cambio de categoría`, `Notas actualizadas`, `Incidencia cerrada`, `Clasificación confirmada`.
- Al cerrar una incidencia se fija `resuelto_en` y se calcula `tiempo_resolucion_minutos`; si se vuelve a Abierta, se limpia `resuelto_en`.

### Evaluación con datos reales

`GET /api/ia/evaluacion` compara la **categoría sugerida** contra la **categoría real** de cada incidencia (verdad de referencia) y calcula: precisión global, cobertura, aciertos/errores, precisión sobre las confirmadas y desglose por fuente y por categoría. Nada se inventa: todo sale de filas almacenadas.

---

## Documentación de la API

Base: `http://localhost:8000/api` · Docs interactivos: `/docs`

Todos los errores devuelven `{"detail": "mensaje"}`.

### Incidencias

**`POST /api/incidencias`** → `201` — crear y clasificar con IA.

```json
{
  "titulo": "No puedo iniciar sesión",
  "descripcion": "El usuario reporta que la cuenta queda bloqueada al intentar entrar...",
  "categoria_id": 1,
  "prioridad_id": 3,
  "creado_por": "Ana"
}
```

Respuesta (detalle completo): `id`, `titulo`, `descripcion`, `categoria`, `prioridad`, `estado`, `creado_en`, `actualizado_en`, `creado_por`, `notas`, `tiempo_resolucion_minutos`, `resuelto_en`, `analisis_ia`, `historial`.

**`GET /api/incidencias`** — listar con filtros y paginación.

Query params: `skip` (0), `limit` (1–100, defecto 20), `estado_id`, `prioridad_id`, `categoria_id` (CSV: `1,3`), `date_from`, `date_to`, `search` (título/descripción), `sort_by` (`creado_en`, `actualizado_en`, `prioridad`, `id`, `titulo`), `order` (`asc`/`desc`).

```json
{ "total": 137, "skip": 0, "limit": 20, "items": [ { "id": 137, "titulo": "...", "estado": "Abierta", "prioridad": "Media", "categoria": "Acceso", "nivel_prioridad": 2, "creado_en": "...", "actualizado_en": "..." } ] }
```

**`GET /api/incidencias/{id}`** → detalle completo (análisis IA + historial). `404` si no existe.

**`PUT /api/incidencias/{id}`** — actualizar (registra historial). Campos opcionales:

```json
{ "estado_id": 3, "prioridad_id": 2, "categoria_id": 2, "notas": "Resuelto por soporte", "creado_por": "Sistema Demo" }
```

**`PUT /api/incidencias/{id}/analisis-ia/confirmar`** — confirmar/retirar clasificación:

```json
{ "confirmado": true }
```

### Analítica (todas `GET`; `period` = `7d` | `30d` | `90d`, o `date_from`/`date_to` con `period=custom`)

| Ruta | Contenido |
| --- | --- |
| `/api/analitica/metricas` | KPIs + `comparison` (cambios % vs período anterior) |
| `/api/analitica/por-categoria` | `categorias[]` con total/abiertas/cerradas/porcentaje/color |
| `/api/analitica/tendencia?granularity=daily\|hourly` | serie `date, created, closed, opened` |
| `/api/analitica/tiempo-resolucion` | promedio/mediana/min/max/P95 + por categoría y prioridad |

### IA

| Ruta | Descripción |
| --- | --- |
| `POST /api/ia/preguntar` | body `{"pregunta": "..."}` → asistente en lenguaje natural |
| `GET /api/ia/perspectivas?limit=4&period=7d` | perspectivas automáticas con cambios reales |
| `GET /api/ia/evaluacion` | precisión real del clasificador (global, por fuente, por categoría) |

### Health

**`GET /api/health`**

```json
{ "status": "ok", "service": "IncidenciaIQ", "version": "1.2.0" }
```

---

## Tests

```bash
cd backend
pytest                     # 12 tests pasan (FastAPI TestClient: CRUD, analítica, IA, clasificador y SPA)
```

---

## Despliegue en Render + Neon

La forma más económica de llevar esto a un entorno real: **un solo Web Service** en Render (FastAPI sirve API + frontend) con **Postgres gratis de Neon** (la Postgres gratuita de Render expira a los 30 días).

### 1. Repositorio

Sube el proyecto a GitHub. El `Dockerfile` de la raíz ya es multi-stage:

1. Compila el frontend (`node:20-alpine` → `npm run build`).
2. Copia el backend, instala `requirements.txt` y copia `dist/`.
3. Ejecuta `uvicorn app.main:app --port ${PORT:-8000}` (escucha en el puerto que inyecte la plataforma).

### 2. Base de datos en Neon

1. Entra en [neon.tech](https://neon.tech) → New Project.
2. En **Connect** elige la pestaña **Pooled connection**.
3. Copia la cadena (termina en `-pooler.neon.tech`); si no incluye `?sslmode=require`, añádela.

### 3. Crear el Web Service en Render

1. En [render.com](https://render.com): **New → Web Service** → conecta el repo.
2. Build & Deploy: Render detecta el `Dockerfile` (Root Directory: raíz del repo). Plan: **Free**.
3. **Environment → Variables**:

| Variable | Valor |
| --- | --- |
| `DATABASE_URL` | la cadena **pooled** de Neon con `?sslmode=require` |
| `OPENAI_API_KEY` | tu key (opcional; sin key usa heurística) |
| `SEMBRAR_DEMO_DATA` | `false` para empezar limpio, o `true` para las 130 demo |
| `API_CORS_ORIGINS` | tu URL `https://<app>.onrender.com` (o déjala vacía: same-origin) |
| `ENVIRONMENT` | `production` |
| `API_DEBUG` | `false` |

4. (Opcional) Health Check Path: `/api/health`.
5. **Deploy**. La primera vez tarda unos minutos (compila npm + pip en el contenedor).

### Limitaciones del plan gratuito

- El Web Service **duerme** tras 15 min sin tráfico y reacciona en ~1 min (primer request).
- 750 h de cómputo / mes (las horas dormidas no cuentan).
- No hay disco persistente: toda la persistencia está en Postgres (Neon), nunca en el filesystem.
- Neon escala a 0 tras 5 min de inactividad (primera consulta ~0,5 s; la app usa `pool_pre_ping`).

---

## Docker

Imagen multi-stage (repositorio completo: frontend + backend):

```bash
docker build -t incidentiq .
docker run --rm -p 8000:8000 -e DATABASE_URL="postgresql+psycopg://..." incidentiq
```

Solo backend + Postgres para desarrollo (depende del `.env` local):

```bash
cd backend
docker compose up --build
```

---

## Solución de problemas

| Problema | Causa / solución |
| --- | --- |
| `ModuleNotFoundError: No module named 'psycopg2'` | La `DATABASE_URL` llegó sin driver. La app ya la normaliza (`postgresql://` → `postgresql+psycopg://`); en despliegues antiguos basta cambiar manualmente el prefijo. |
| `GET /api/health` devuelve HTML | Orden de rutas roto (el catch-all SPA captura `/api/*`). Todo router y `/api/health` debe registrarse **antes** de `_montar_frontend()`. |
| Sin incidencias al abrir | `SEMBRAR_DEMO_DATA=false` → Punto previsto. Crea una desde la UI o siembra con `true`. |
| La IA responde genérico | `OPENAI_API_KEY` vacía → funciona en modo heurístico (revisa `fuente` en el detalle). |
| `Failed to connect` en dev | Levantar el backend (`:8000`) antes que el frontend (`:5173`). |

---

## Roadmap

- [x] CRUD de incidencias con historial y auditoría
- [x] Clasificación IA explicable (LLM + reglas + casos TF-IDF)
- [x] Evaluación real del clasificador
- [x] Analítica con comparación de períodos
- [x] AI Help y perspectivas automáticas
- [x] UI en español (React + Tailwind)
- [x] Despliegue single-service en contenedor
- [ ] Autenticación y roles de usuario
- [ ] Rate limiting en endpoints de IA
- [ ] Migraciones con Alembic
- [ ] Backups automáticos de Postgres

---

## Licencia

Uso interno / demostración. No afiliado a ni avalado por OpenAI.
