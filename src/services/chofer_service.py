"""Chofer (driver) business logic with Spanish validation messages."""

from typing import Optional

from src.db import execute, fetch_all, fetch_one, now_iso


class ChoferService:
    """CRUD operations and validation for choferes."""

    def _cedula_exists(self, cedula: str, exclude_id: Optional[int] = None) -> bool:
        if exclude_id is not None:
            row = fetch_one(
                "SELECT id FROM choferes WHERE UPPER(cedula) = UPPER(?) AND id != ?",
                (cedula, exclude_id),
            )
        else:
            row = fetch_one(
                "SELECT id FROM choferes WHERE UPPER(cedula) = UPPER(?)", (cedula,)
            )
        return row is not None

    def create_chofer(self, nombre: str, cedula: str, licencia: str, telefono: str) -> int:
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("El nombre es obligatorio.")
        if len(nombre) > 200:
            raise ValueError("El nombre no puede superar los 200 caracteres.")
        cedula = (cedula or "").strip() or None
        if cedula is not None and self._cedula_exists(cedula):
            raise ValueError("Ya existe un chofer con esa cédula.")
        return execute(
            "INSERT INTO choferes (nombre, cedula, licencia, telefono, estado, created_at) VALUES (?, ?, ?, ?, 'activo', ?)",
            (nombre, cedula, licencia, telefono, now_iso()),
        )

    def list_choferes(self, q: str = "") -> list[dict]:
        """List choferes, optionally filtered by nombre or cédula."""
        if q:
            pattern = f"%{q}%"
            rows = fetch_all(
                "SELECT * FROM choferes WHERE nombre LIKE ? OR cedula LIKE ? ORDER BY nombre COLLATE NOCASE",
                (pattern, pattern),
            )
        else:
            rows = fetch_all("SELECT * FROM choferes ORDER BY nombre COLLATE NOCASE")
        return [dict(row) for row in rows]

    def get_chofer(self, chofer_id: int) -> Optional[dict]:
        row = fetch_one("SELECT * FROM choferes WHERE id = ?", (chofer_id,))
        return dict(row) if row else None

    def update_chofer(self, chofer_id: int, data: dict) -> None:
        nombre = (data.get("nombre") or "").strip()
        if not nombre:
            raise ValueError("El nombre es obligatorio.")
        if len(nombre) > 200:
            raise ValueError("El nombre no puede superar los 200 caracteres.")
        cedula = (data.get("cedula") or "").strip() or None
        if cedula is not None and self._cedula_exists(cedula, exclude_id=chofer_id):
            raise ValueError("Ya existe un chofer con esa cédula.")
        execute(
            "UPDATE choferes SET nombre = ?, cedula = ?, licencia = ?, telefono = ?, estado = ? WHERE id = ?",
            (nombre, cedula, data.get("licencia") or None, data.get("telefono") or None, data.get("estado") or "activo", chofer_id),
        )

    def delete_chofer(self, chofer_id: int) -> None:
        execute("DELETE FROM choferes WHERE id = ?", (chofer_id,))

    def count_choferes(self) -> int:
        row = fetch_one("SELECT COUNT(*) AS total FROM choferes")
        return int(row["total"]) if row else 0


chofer_service = ChoferService()
