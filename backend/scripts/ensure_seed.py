"""Si la DB está vacía, restaura el dump incluido (schema + datos + traducciones).

El dump se generó con --no-owner --no-privileges desde la BD local, que ya
contiene las 29 recetas finales (nombres sin 'Panameña', 4 sin foto eliminadas).
"""

import subprocess

import psycopg2

from app.core.config import settings

DUMP_PATH = "/app/data/resazon_dump.dump"


def _recipes_count(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM recipes")
        return cur.fetchone()[0]


def main() -> int:
    url = settings.DATABASE_URL.replace("+psycopg2", "").replace("postgresql://", "postgres://", 1)
    try:
        conn = psycopg2.connect(url, connect_timeout=5)
    except Exception as exc:  # noqa: BLE001
        print(f"[ensure_seed] No pude conectar: {exc}")
        return 1

    try:
        if _recipes_count(conn) > 0:
            print("[ensure_seed] DB ya poblada, no hago nada.")
            return 0
    except Exception as exc:  # noqa: BLE001
        print(f"[ensure_seed] ¿Schema aún sin crear? ({exc}); intentando restaurar igualmente.")
    finally:
        conn.close()

    if not __import__("os").path.exists(DUMP_PATH):
        print(f"[ensure_seed] No existe {DUMP_PATH}; dejo la BD vacía (alembic creará el schema).")
        return 0

    print(f"[ensure_seed] DB vacía → restaurando {DUMP_PATH}...")
    proc = subprocess.run(
        ["pg_restore", "--no-owner", "--no-privileges", "--exit-on-error", "-d", url, DUMP_PATH],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(f"[ensure_seed] pg_restore falló:\n{proc.stdout}\n{proc.stderr}")
        return proc.returncode
    print("[ensure_seed] Restauración completada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())