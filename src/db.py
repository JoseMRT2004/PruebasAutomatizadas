"""SQLite database access layer using the standard library."""

import sqlite3
import threading
from datetime import datetime

from src.config import settings

_connection: sqlite3.Connection | None = None
_lock = threading.Lock()


def get_connection() -> sqlite3.Connection:
    """Return the module-level SQLite connection, creating it on first use."""
    global _connection
    with _lock:
        if _connection is None:
            _connection = sqlite3.connect(settings.app_db_path, check_same_thread=False)
            _connection.row_factory = sqlite3.Row
        return _connection


def fetch_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    """Execute a SELECT query and return all matching rows."""
    conn = get_connection()
    with _lock:
        return conn.execute(sql, params).fetchall()


def fetch_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    """Execute a SELECT query and return a single row or None."""
    conn = get_connection()
    with _lock:
        return conn.execute(sql, params).fetchone()


def execute(sql: str, params: tuple = ()) -> int:
    """Execute a write query, commit, and return the last inserted row id."""
    conn = get_connection()
    with _lock:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.lastrowid


def init_db() -> None:
    """Create all tables if they do not exist."""
    conn = get_connection()
    with _lock:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS choferes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cedula TEXT UNIQUE,
                licencia TEXT,
                telefono TEXT,
                estado TEXT NOT NULL DEFAULT 'activo',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS camiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                placa TEXT UNIQUE NOT NULL,
                marca TEXT,
                modelo TEXT,
                anio INTEGER,
                capacidad INTEGER,
                estado TEXT NOT NULL DEFAULT 'activo',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS rutas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origen TEXT NOT NULL,
                destino TEXT NOT NULL,
                distancia_km REAL NOT NULL,
                duracion_min INTEGER,
                estado TEXT NOT NULL DEFAULT 'activa',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS horas_trabajo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chofer_id INTEGER NOT NULL REFERENCES choferes(id),
                ruta_id INTEGER NOT NULL REFERENCES rutas(id),
                fecha TEXT NOT NULL,
                horas REAL NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.commit()


def close_connection() -> None:
    """Close the module-level connection, if open."""
    global _connection
    with _lock:
        if _connection is not None:
            _connection.close()
            _connection = None


def now_iso() -> str:
    """Return the current datetime as an ISO 8601 string."""
    return datetime.now().isoformat()
