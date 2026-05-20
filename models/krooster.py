from __future__ import annotations

from pydantic import BaseModel, RootModel, Field

# ========================= SHARED =========================

class Ingredient(BaseModel):
    id: str
    quantity: int

# ========================= OPERATORS =========================

class Branch(BaseModel):
    id: str
    name: str


class Mastery(BaseModel):
    masteryLevel: int
    ingredients: list[Ingredient]
    name: str
    category: int


class SkillDatum(BaseModel):
    skillId: str
    iconId: str | None
    skillName: str
    masteries: list[Mastery]


class Stage(BaseModel):
    moduleLevel: int
    ingredients: list[Ingredient]
    name: str
    category: int


class ModuleDatum(BaseModel):
    moduleName: str
    moduleId: str
    typeName: str
    stages: list[Stage]
    isCnOnly: bool


class SkillLevel(BaseModel):
    skillLevel: int
    ingredients: list[Ingredient]
    name: str
    category: int


class EliteLevel(BaseModel):
    eliteLevel: int
    ingredients: list[Ingredient]
    name: str
    category: int


class Operator(BaseModel, serialize_by_alias=True):
    id: str
    name: str
    cnName: str
    rarity: int
    class_: str = Field(..., alias='class')
    branch: Branch
    isCnOnly: bool
    factions: list[str]
    pools: list[str]
    skillData: list[SkillDatum]
    moduleData: list[ModuleDatum]
    potentials: list[str]
    skillLevels: list[SkillLevel]
    eliteLevels: list[EliteLevel]
    factionsHidden: list[str] | None = None


class OperatorDict(RootModel[dict[str, Operator]]):
    pass

# ========================= ITEMS =========================

class Item(BaseModel, serialize_by_alias=True):
    id: str
    name: str
    iconId: str
    tier: int
    sortId: int
    ingredients: list[Ingredient] | None = None
    yield_: int | None = Field(None, alias='yield')


class ItemDict(RootModel[dict[str, Item]]):
    pass

# ========================= VALIDATIONS =========================

def validate_file(filepath, model):
    import json
    with open(filepath, 'r') as file:
        json_data = json.load(file)
        model.model_validate(json_data)

if __name__ == '__main__':
    validate_file('data/operators.json', OperatorDict)
    validate_file('data/items-krooster.json', ItemDict)
