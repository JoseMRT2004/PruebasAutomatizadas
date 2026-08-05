"""HoraTrabajo (work hours) business logic with Spanish validation messages."""

from src.db import execute, fetch_all, fetch_one, now_iso


class HoraService:
    """Registration and queries for work hours, joining choferes and rutas."""

    def create_hora(self, chofer_id, ruta_id, fecha: str, horas) -> int:
        try:
            chofer_id = int(chofer_id)
        except (TypeError, ValueError):
            raise ValueError("El chofer seleccionado no existe.")
        try:
            ruta_id = int(ruta_id)
        except (TypeError, ValueError):
            raise ValueError("La ruta seleccionada no existe.")
        if fetch_one("SELECT id FROM choferes WHERE id = ?", (chofer_id,)) is None:
            raise ValueError("El chofer seleccionado no existe.")
        if fetch_one("SELECT id FROM rutas WHERE id = ?", (ruta_id,)) is None:
            raise ValueError("La ruta seleccionada no existe.")
        fecha = (fecha or "").strip()
        if not fecha:
            raise ValueError("La fecha es obligatoria.")
        try:
            horas = float(horas)
        except (TypeError, ValueError):
            raise ValueError("Las horas deben estar entre 1 y 24.")
        if not (1 <= horas <= 24):
            raise ValueError("Las horas deben estar entre 1 y 24.")
        return execute(
            "INSERT INTO horas_trabajo (chofer_id, ruta_id, fecha, horas, created_at) VALUES (?, ?, ?, ?, ?)",
            (chofer_id, ruta_id, fecha, horas, now_iso()),
        )

    def list_horas(self) -> list[dict]:
        """List work hours joined with the chofer name and ruta label."""
        rows = fetch_all(
            """
            SELECT h.*, c.nombre AS chofer_nombre, r.origen AS ruta_origen, r.destino AS ruta_destino
            FROM horas_trabajo h
            JOIN choferes c ON c.id = h.chofer_id
            JOIN rutas r ON r.id = h.ruta_id
            ORDER BY h.fecha DESC, h.id DESC
            """
        )
        result = []
        for row in rows:
            item = dict(row)
            item["ruta_label"] = f"{item['ruta_origen']} → {item['ruta_destino']}"
            result.append(item)
        return result

    def delete_hora(self, hora_id: int) -> None:
        execute("DELETE FROM horas_trabajo WHERE id = ?", (hora_id,))

    def count_horas(self) -> int:
        row = fetch_one("SELECT COUNT(*) AS total FROM horas_trabajo")
        return int(row["total"]) if row else 0

    def get_choferes_choices(self) -> list[dict]:
        """Return chofer id/name pairs for form selects."""
        rows = fetch_all("SELECT id, nombre FROM choferes ORDER BY nombre COLLATE NOCASE")
        return [{"id": row["id"], "nombre": row["nombre"]} for row in rows]

    def get_rutas_choices(self) -> list[dict]:
        """Return ruta id/label pairs (``origen → destino``) for form selects."""
        rows = fetch_all("SELECT id, origen, destino FROM rutas ORDER BY origen COLLATE NOCASE")
        return [
            {"id": row["id"], "label": f"{row['origen']} → {row['destino']}"}
            for row in rows
        ]


hora_service = HoraService()
