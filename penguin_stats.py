from typing import Any

import requests

from utils import cached
from models.penguin_stats import StageList, ItemList, DropMatrix, Stage, FarmingPlan, Item

import logging
logger = logging.getLogger(__name__)

SERVER = 'CN'
API_BASE = 'https://penguin-stats.io/PenguinStats/api/v2'
PLANNER_URL = 'https://planner.penguin-stats.io/plan'

@cached('data/stages.json', StageList)
def load_stages() -> StageList:
    logger.info('Loading stages...')
    json_data: dict[str, Any] = requests.get(API_BASE + '/stages').json()
    stages: StageList = StageList.model_validate(json_data)
    logger.info(f'{len(stages.root)} stages loaded.')
    return stages

def get_stage_map() -> dict[str, Stage]:
    stages: StageList = load_stages()
    return {
        stage.stageId: stage
        for stage in stages.root
    }

def get_stage_code_map() -> dict[str, list[str]]:
    stages: StageList = load_stages()
    code_map: dict[str, list[str]] = {}

    for stage in stages.root:
        stage_code: str = stage.code
        stage_id: str = stage.stageId

        if stage_code not in code_map:
            code_map[stage_code] = []

        code_map[stage_code].append(stage_id)

    return code_map

def convert_stage_codes(stage_codes: list[str]) -> list[str]:
    stage_code_map: dict[str, list[str]] = get_stage_code_map()
    stage_ids: list[str] = []

    for code in stage_codes:
        if code not in stage_code_map:
            logger.warning(f'Stage {code} not found, skipping')
            continue

        ids: list[str] = stage_code_map[code]
        stage_ids.extend(ids)

        if len(ids) > 1:
            logger.info(f'Stage {code} has ambiguous ids {ids}, adding both')

    return stage_ids

@cached('data/items_penguin_stats.json', ItemList)
def load_items() -> ItemList:
    logger.info('Loading items...')
    json_data: dict[str, Any] = requests.get(API_BASE + '/items').json()
    items: ItemList = ItemList.model_validate(json_data)
    logger.info(f'{len(items.root)} items loaded.')
    return items

def get_item_map() -> dict[str, Item]:
    items: ItemList = load_items()
    return {
        item.itemId: item
        for item in items.root
    }

def get_drop_matrix(stage_ids: list[str]) -> DropMatrix:
    assert len(stage_ids) > 0

    logger.info('Loading stage drops matrix...')
    url: str = API_BASE + '/result/matrix'
    params: dict[str, Any] = {
        'server': SERVER,
        'stageFilter': ','.join(stage_ids),
        'show_closed_zones': True,
    }
    json_data: dict[str, Any] = requests.get(url, params=params).json()
    drop_matrix: DropMatrix = DropMatrix.model_validate(json_data)
    logger.info(f'{len(drop_matrix.matrix)} eles loaded.')
    return drop_matrix

def get_farming_plan(owned: dict[str, int],
                     required: dict[str, int],
                     exclude: list[str] = []) -> FarmingPlan:
    payload: dict[str, Any] = {
        'owned': owned,
        'required': required,
        'exclude': exclude,
        'exp_demand': False,
        'gold_demand': False,
        'extra_outc': False,
        'input_lang': 'id',
        'output_lang': 'id',
        'server': SERVER,
    }

    logger.info('Loading farming plan...')
    json_data: dict[str, Any] = requests.post(PLANNER_URL, json=payload).json()
    farming_plan: FarmingPlan = FarmingPlan.model_validate(json_data)
    logger.info(f'{len(farming_plan.stages)} stages, {len(farming_plan.syntheses)} syntheses loaded')
    return farming_plan

def main():
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    load_stages()
    load_items()

if __name__ == '__main__':
    main()
