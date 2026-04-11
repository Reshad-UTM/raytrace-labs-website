import os
from pathlib import Path

# Detect environment
DATABASE_URL = os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # 🔵 Production (Vercel → Postgres)
    import psycopg2
    from psycopg2.extras import RealDictCursor

    def get_connection():
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

    def query_all(sql, params=()):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        finally:
            conn.close()

    def query_one(sql, params=()):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchone()
        finally:
            conn.close()

    def execute_query(sql, params=()):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                conn.commit()
        finally:
            conn.close()

else:
    # 🟢 Local (SQLite)
    import sqlite3

    BASE_DIR = Path(__file__).resolve().parent
    DB_PATH = BASE_DIR / "raytrace.db"

    def get_connection():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def query_all(sql, params=()):
        conn = get_connection()
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()

    def query_one(sql, params=()):
        conn = get_connection()
        try:
            return conn.execute(sql, params).fetchone()
        finally:
            conn.close()

    def execute_query(sql, params=()):
        conn = get_connection()
        try:
            conn.execute(sql, params)
            conn.commit()
        finally:
            conn.close()