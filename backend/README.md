# ReSazón Loop — Backend

API de recetas panameñas con detección de ingredientes por imagen.
**FastAPI + PostgreSQL/pgvector + Gemini (Vision, generación y embeddings).**

## Requisitos

- Python 3.12+
- Docker (PostgreSQL 16 + pgvector vía `docker-compose.yml`)
- Una `GEMINI_API_KEY`

## Setup

```bash
# 1. Base de datos
docker compose up -d          # Postgres 16 + pgvector (puerto 5432)

# 2. Entorno y dependencias
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Configuración
cp .env.example .env          # pega tu GEMINI_API_KEY (el .env nunca se sube)

# 4. Migraciones + seed
.venv/bin/alembic upgrade head
.venv/bin/python -m scripts.seed_db

# 5. Ingesta del recetario al RAG
#    Coloca tu recetario en data/raw/ y ejecuta:
.venv/bin/python -m scripts.ingest_recetario

# 6. Servidor
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Docs interactivas en `http://localhost:8000/docs`.

## Endpoints principales

| Método | Ruta | Propósito |
|---|---|---|
| POST | `/api/v1/scan` | Sube imagen → ingredientes detectados (Gemini Vision + normalización) |
| POST | `/api/v1/ingredients/confirm` | Confirma/edita la lista detectada |
| POST | `/api/v1/recipes/search` | Recetas tradicionales panameñas por ingredientes (RAG + matcher) |
| POST | `/api/v1/recipes/generate` | "Crear con mis ingredientes" (Gemini guiado por RAG) |
| POST | `/api/v1/recipes/healthy` | Versión saludable de referencia panameña |
| GET | `/api/v1/recipes` | Listado paginado |
| GET | `/api/v1/recipes/{id}` | Detalle completo |
| POST | `/api/v1/rag/search` | Búsqueda semántica (debug interno) |
| GET | `/api/v1/health` | Healthcheck |

Toda respuesta viaja en `{"data": ...}`; los errores en `{"code","message","details"}`.

## Estructura

```
app/
├── core/           Config, seguridad, logging, excepciones, DB
├── api/v1/         Routers finos (sin lógica de negocio)
├── models/         SQLAlchemy ORM (12 tablas)
├── schemas/        Pydantic (contratos de entrada/salida)
├── services/       Casos de uso (orquestan todo)
├── repositories/   Única capa que consulta la DB
├── vision/         Gemini Vision + normalización de ingredientes
├── ai/             Cliente Gemini único + prompts versionados + parser
├── rag/            Ingesta, embeddings, vector store, retriever
├── recipes/        Lógica pura: matcher, ranker, assembler
└── nutrition/      Estimador heurístico de macros
scripts/            ingesta + seed
tests/              pytest (unit + integración)
```

## Seguridad

- `backend/.env` con tu `GEMINI_API_KEY` está **ignorado por git** (regla en el
  `.gitignore` raíz y de `backend/`). Solo se versiona `backend/.env.example`.
- La API key vive únicamente en el backend; ningún cliente la recibe.
- `core/security.py` valida MIME y tamaño de imágenes antes de tocar cualquier servicio.

## Notas

- El recetario se asume en `data/raw/Recetario_Nuestro_Sabor_Panama_estructurado.txt`.
  El parser detecta automáticamente el formato del PDF estructurado (bloques
  `=== PÁGINA N ===` con pasos numerados, ingredientes `-` y título duplicado)
  y, como alternativa, la heurística genérica por títulos/secciones/`INGREDIENTES:`.
- La información nutricional es **estimada** (`is_estimated=true`) y no es consejo médico.
- `Recipe.type` distingue `traditional` | `ai_generated` | `ai_adapted`.