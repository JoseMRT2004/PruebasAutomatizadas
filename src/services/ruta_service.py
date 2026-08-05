"""Ruta (route) business logic with Spanish validation messages."""

from typing import Optional

from src.db import execute, fetch_all, fetch_one, now_iso


class RutaService:
    """CRUD operations and validation for rutas."""

    @staticmethod
    def _parse_optional_int(value, message: str) -> Optional[int]:
        if value is None or str(value).strip() == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(message)

    def create_ruta(self, origen: str, destino: str, distancia_km, duracion_min) -> int:
        origen = (origen or "").strip()
        if not origen:
            raise ValueError("El origen es obligatorio.")
        destino = (destino or "").strip()
        if not destino:
            raise ValueError("El destino es obligatorio.")
        try:
            distancia_km = float(distancia_km)
        except (TypeError, ValueError):
            raise ValueError("La distancia debe ser mayor que 0 y no superar 5000 km.")
        if not (0 < distancia_km <= 5000):
            raise ValueError("La distancia debe ser mayor que 0 y no superar 5000 km.")
        duracion_min = self._parse_optional_int(duracion_min, "La duración debe ser un número entero.")
        return execute(
            "INSERT INTO rutas (origen, destino, distancia_km, duracion_min, estado, created_at) VALUES (?, ?, ?, ?, 'activa', ?)",
            (origen, destino, distancia_km, duracion_min, now_iso()),
        )

    def list_rutas(self, q: str = "") -> list[dict]:
        """List rutas, optionally filtered by origen or destino."""
        if q:
            pattern = f"%{q}%"
            rows = fetch_all(
                "SELECT * FROM rutas WHERE origen LIKE ? OR destino LIKE ? ORDER BY origen COLLATE NOCASE",
                (pattern, pattern),
            )
        else:
            rows = fetch_all("SELECT * FROM rutas ORDER BY origen COLLATE NOCASE")
        return [dict(row) for row in rows]

    def get_ruta(self, ruta_id: int) -> Optional[dict]:
        row = fetch_one("SELECT * FROM rutas WHERE id = ?", (ruta_id,))
        return dict(row) if row else None

    def update_ruta(self, ruta_id: int, data: dict) -> None:
        origen = (data.get("origen") or "").strip()
        if not origen:
            raise ValueError("El origen es obligatorio.")
        destino = (data.get("destino") or "").strip()
        if not destino:
            raise ValueError("El destino es obligatorio.")
        try:
            distancia_km = float(data.get("distancia_km"))
        except (TypeError, ValueError):
            raise ValueError("La distancia debe ser mayor que 0 y no superar 5000 km.")
        if not (0 < distancia_km <= 5000):
            raise ValueError("La distancia debe ser mayor que 0 y no superar 5000 km.")
        duracion_min = self._parse_optional_int(data.get("duracion_min"), "La duración debe ser un número entero.")
        execute(
            "UPDATE rutas SET origen = ?, destino = ?, distancia_km = ?, duracion_min = ?, estado = ? WHERE id = ?",
            (origen, destino, distancia_km, duracion_min, data.get("estado") or "activa", ruta_id),
        )

    def delete_ruta(self, ruta_id: int) -> None:
        execute("DELETE FROM rutas WHERE id = ?", (ruta_id,))

    def count_rutas(self) -> int:
        row = fetch_one("SELECT COUNT(*) AS total FROM rutas")
        return int(row["total"]) if row else 0


ruta_service = RutaService()
