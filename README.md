# IncidentIQ

Plataforma web SaaS de monitoreo inteligente de incidencias. Permite centralizar, registrar, clasificar y analizar incidencias operativas usando una API REST, PostgreSQL y un agente de IA que genera análisis automáticos.

## Stack

- **Backend**: Python · FastAPI · SQLAlchemy · PostgreSQL
- **Frontend**: React · Vite · Tailwind CSS · Recharts
- **IA**: OpenAI ChatGPT API (con clasificador heurístico offline como fallback)
- **Despliegue**: Docker · Render/Railway (API) · Vercel (frontend)

## Estructura

```
backend/
  app/
    main.py            # App FastAPI + CORS + health
    configuracion.py   # Configuración por env vars
    base_de_datos.py   # Engine + sesiones SQLAlchemy
    models/            # ORM: Incidencia, Categoria, Prioridad, Estado, AnalisisIA, Historial
    schemas/           # Pydantic: incidencia, analitica, ia, error
    services/          # servicio_incidencias, servicio_analitica, servicio_ia
    routers/           # /api/incidencias, /api/analitica, /api/ia
    prompts/           # Prompt engineering para OpenAI
    sembrar.py         # Datos de referencia + incidencias demo
  tests/
frontend/
  src/
    components/        # Disposición, Panel, Incidencias, Analitica, AI, Common
    pages/             # Panel, Incidencias, DetalleIncidencia, Analitica, AyudaIA
    services/          # Clientes axios
    hooks/             # useApi, useIncidencias, useAnalitica, useIA
    constants/         # rutas, categorias, prioridades, estados
```

## Puesta en marcha rápida (local)

### Base de datos (PostgreSQL)

Con Docker:

```bash
cd backend
docker compose up -d db
```

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env          # ajusta DATABASE_URL / API key si es necesario
uvicorn app.main:app --reload --port 8000
```

- Swagger/API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

### Frontend

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173 (proxy `/api` hacia `localhost:8000`)

## IA

Si `OPENAI_API_KEY` está vacía, el sistema usa un clasificador heurístico por palabras clave para que toda la funcionalidad (clasificación, AI Help, perspectivas) funcione sin coste. Para activar ChatGPT, define la API key en `.env`.

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### Sustento de las predicciones (no es "IA de mentira")

Cada sugerencia registra su **origen** (`fuente`) y su **justificación** (`justificacion`):
`openai` (modelo GPT), `heuristic` (reglas por palabras clave), `case` (caso histórico),
`openai_case` / `heuristic_case` (combinaciones). El clasificador combina el modelo CGPT
con un índice **TF-IDF + similitud de coseno** (Python puro, sin librerías pesadas) sobre
incidencias reales resueltas o confirmadas, y guarda `incidencia_referencia_id` +
`indice_similitud`. `GET /api/ia/evaluacion` mide con datos reales la precisión contra la
categoría asignada/confirmada, con desglose por fuente y por categoría.

## Endpoints principales

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/api/health` | Health check |
| POST | `/api/incidencias` | Crear incidencia (clasifica con IA) |
| GET | `/api/incidencias` | Listar con filtros y paginación |
| GET | `/api/incidencias/{id}` | Detalle + análisis IA + historial |
| PUT | `/api/incidencias/{id}` | Actualizar estado/prioridad/notas |
| PUT | `/api/incidencias/{id}/analisis-ia/confirmar` | Confirmar clasificación IA |
| POST | `/api/ia/preguntar` | Preguntas a AI Help en lenguaje natural |
| GET | `/api/ia/perspectivas` | Perspectivas automáticas con cambios reales vs periodo anterior |
| GET | `/api/ia/evaluacion` | Precisión/cobertura reales del clasificador |
| GET | `/api/analitica/metricas` | KPIs con comparación |
| GET | `/api/analitica/por-categoria` | Desglose por categoría |
| GET | `/api/analitica/tendencia` | Tendencia por día/hora |
| GET | `/api/analitica/tiempo-resolucion` | Estadísticas de resolución |

## Docker completo (backend + BD)

```bash
cd backend
docker compose up --build
```

## Tests

```bash
cd backend
pytest
```