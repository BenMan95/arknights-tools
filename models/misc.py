from __future__ import annotations

from pydantic import BaseModel, RootModel, Field

# ========================= DROPS =========================

class DropRate(BaseModel):
    id: str
    rate: float
    start: int
    end: int | None


class StageDrops(BaseModel):
    id: str
    sanity: int
    drops: list[DropRate]


class DropSummary(RootModel[dict[str, StageDrops]]):
    pass
