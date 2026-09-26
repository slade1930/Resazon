"""Espera a que la base de datos esté disponible (para entrypoint)."""

import sys
import time

import psycopg2

from app.core.config import settings

url = settings.DATABASE_URL.replace("+psycopg2", "").replace("postgresql://", "postgres://", 1)

for attempt in range(30):
    try:
        conn = psycopg2.connect(url, connect_timeout=3)
        conn.close()
        print(f"[wait_for_db] DB lista (intento {attempt + 1})")
        sys.exit(0)
    except Exception as exc:  # noqa: BLE001
        print(f"[wait_for_db] intento {attempt + 1}/30: {exc}")
        time.sleep(2)

print("[wait_for_db] No pude conectar a la DB tras 30 intentos.")
sys.exit(1)