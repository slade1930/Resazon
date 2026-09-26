#!/bin/sh
set -e

echo "[entrypoint] Esperando a la base de datos..."
python /app/scripts/wait_for_db.py

echo "[entrypoint] Sembrando datos si la DB está vacía..."
python /app/scripts/ensure_seed.py

echo "[entrypoint] Aplicando migraciones pendientes (alembic upgrade head)..."
alembic upgrade head

echo "[entrypoint] Arrancando uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}