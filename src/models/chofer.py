"""Chofer (driver) data model."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Chofer(BaseModel):
    """A transport driver."""

    id: Optional[int] = None
    nombre: str
    cedula: Optional[str] = None
    licencia: Optional[str] = None
    telefono: Optional[str] = None
    estado: str = "activo"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
