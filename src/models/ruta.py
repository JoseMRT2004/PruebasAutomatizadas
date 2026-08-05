"""Ruta (route) data model."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Ruta(BaseModel):
    """A transport route between two locations."""

    id: Optional[int] = None
    origen: str
    destino: str
    distancia_km: float
    duracion_min: Optional[int] = None
    estado: str = "activa"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
