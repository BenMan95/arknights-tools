from __future__ import annotations

from pydantic import BaseModel, RootModel, Field

# ========================= SHARED =========================

class I18n(BaseModel):
    en: str
    ja: str
    ko: str
    zh: str


class Existence(BaseModel):
    exist: bool
    openTime: int | None = None
    closeTime: int | None = None


class ServerExistence(BaseModel):
    CN: Existence
    JP: Existence
    KR: Existence
    US: Existence

# ========================= STAGES =========================


class Bounds(BaseModel):
    lower: int
    upper: int
    exceptions: list[int] | None = None


class DropInfo(BaseModel):
    itemId: str | None = None
    dropType: str
    bounds: Bounds


class Stage(BaseModel):
    stageId: str
    zoneId: str
    stageType: str
    code: str
    code_i18n: I18n
    apCost: int
    existence: ServerExistence
    minClearTime: int | None
    dropInfos: list[DropInfo] | None = None
    isGacha: bool | None = None
    recognitionOnly: list[str] | None = None


StageList = RootModel[list[Stage]]

# ========================= ITEMS =========================

class Alias(BaseModel):
    ja: list[str] | None = None
    zh: list[str] | None = None


class Item(BaseModel):
    itemId: str
    name: str
    name_i18n: I18n
    existence: ServerExistence
    itemType: str
    sortId: int
    rarity: int
    groupID: str | None
    spriteCoord: list[int] | None = None
    alias: Alias
    pron: Alias


ItemList = RootModel[list[Item]]

# ========================= MATRIX =========================

class MatrixItem(BaseModel):
    stageId: str
    itemId: str
    times: int
    quantity: int
    stdDev: float
    start: int
    end: int | None


class Matrix(BaseModel):
    matrix: list[MatrixItem]

# ========================= GOALS =========================

class Goal(BaseModel):
    id: str
    have: int
    need: int


class PlannerConfig(BaseModel, serialize_by_alias=True):
    field_type: str = Field(..., alias='@type')
    items: list[Goal]

# ========================= VALIDATIONS =========================

def validate_file(filepath, model):
    import json
    with open(filepath, 'r') as file:
        json_data = json.load(file)
        model.model_validate(json_data)

if __name__ == '__main__':
    validate_file('data/stages.json', StageList)
    validate_file('data/items-penguin-stats.json', ItemList)
