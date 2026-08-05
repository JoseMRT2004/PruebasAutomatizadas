"""HoraTrabajo (work hours) data model."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HoraTrabajo(BaseModel):
    """Work hours logged by a chofer on a ruta for a given date."""

    id: Optional[int] = None
    chofer_id: int
    ruta_id: int
    fecha: str
    horas: float
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
