"""Camion (truck) data model."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Camion(BaseModel):
    """A truck in the fleet."""

    id: Optional[int] = None
    placa: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    capacidad: Optional[int] = None
    estado: str = "activo"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
