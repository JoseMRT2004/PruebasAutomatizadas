"""Camion (truck) business logic with Spanish validation messages."""

from typing import Optional

from src.db import execute, fetch_all, fetch_one, now_iso


class CamionService:
    """CRUD operations and validation for camiones."""

    @staticmethod
    def _parse_optional_int(value, message: str) -> Optional[int]:
        if value is None or str(value).strip() == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(message)

    def _placa_exists(self, placa: str, exclude_id: Optional[int] = None) -> bool:
        if exclude_id is not None:
            row = fetch_one(
                "SELECT id FROM camiones WHERE UPPER(placa) = UPPER(?) AND id != ?",
                (placa, exclude_id),
            )
        else:
            row = fetch_one(
                "SELECT id FROM camiones WHERE UPPER(placa) = UPPER(?)", (placa,)
            )
        return row is not None

    def create_camion(self, placa: str, marca: str, modelo: str, anio, capacidad) -> int:
        placa = (placa or "").strip()
        if not placa:
            raise ValueError("La placa es obligatoria.")
        if self._placa_exists(placa):
            raise ValueError("Ya existe un camión con esa placa.")
        marca = (marca or "").strip() or None
        modelo = (modelo or "").strip() or None
        anio = self._parse_optional_int(anio, "El año debe ser un número entero.")
        capacidad = self._parse_optional_int(capacidad, "La capacidad debe ser un número entero.")
        return execute(
            "INSERT INTO camiones (placa, marca, modelo, anio, capacidad, estado, created_at) VALUES (?, ?, ?, ?, ?, 'activo', ?)",
            (placa, marca, modelo, anio, capacidad, now_iso()),
        )

    def list_camiones(self, q: str = "") -> list[dict]:
        """List camiones, optionally filtered by placa or marca."""
        if q:
            pattern = f"%{q}%"
            rows = fetch_all(
                "SELECT * FROM camiones WHERE placa LIKE ? OR marca LIKE ? ORDER BY placa COLLATE NOCASE",
                (pattern, pattern),
            )
        else:
            rows = fetch_all("SELECT * FROM camiones ORDER BY placa COLLATE NOCASE")
        return [dict(row) for row in rows]

    def get_camion(self, camion_id: int) -> Optional[dict]:
        row = fetch_one("SELECT * FROM camiones WHERE id = ?", (camion_id,))
        return dict(row) if row else None

    def update_camion(self, camion_id: int, data: dict) -> None:
        placa = (data.get("placa") or "").strip()
        if not placa:
            raise ValueError("La placa es obligatoria.")
        if self._placa_exists(placa, exclude_id=camion_id):
            raise ValueError("Ya existe un camión con esa placa.")
        anio = self._parse_optional_int(data.get("anio"), "El año debe ser un número entero.")
        capacidad = self._parse_optional_int(data.get("capacidad"), "La capacidad debe ser un número entero.")
        execute(
            "UPDATE camiones SET placa = ?, marca = ?, modelo = ?, anio = ?, capacidad = ?, estado = ? WHERE id = ?",
            (
                placa,
                (data.get("marca") or "").strip() or None,
                (data.get("modelo") or "").strip() or None,
                anio,
                capacidad,
                data.get("estado") or "activo",
                camion_id,
            ),
        )

    def delete_camion(self, camion_id: int) -> None:
        execute("DELETE FROM camiones WHERE id = ?", (camion_id,))

    def count_camiones(self) -> int:
        row = fetch_one("SELECT COUNT(*) AS total FROM camiones")
        return int(row["total"]) if row else 0


camion_service = CamionService()
