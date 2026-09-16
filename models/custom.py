from __future__ import annotations

from pydantic import BaseModel


class StageEfficiency(BaseModel):
    efficiency: float
    main_drop: str
    main_drop_efficiency: float
