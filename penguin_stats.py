import requests

from utils import cached
from models.penguin_stats import StageList, ItemList, DropMatrix, Stage, FarmingPlan, Item
from models.misc import DropRate, StageDrops, DropSummary

import logging
logger = logging.getLogger(__name__)

SERVER = 'CN'
API_BASE = 'https://penguin-stats.io/PenguinStats/api/v2'
PLANNER_URL = 'https://planner.penguin-stats.io/plan'

@cached('data/stages.json', StageList)
def load_stages() -> StageList:
    logger.info('Loading stages...')
    json_data = requests.get(API_BASE + '/stages').json()
    stages = StageList.model_validate(json_data)
    logger.info(f'{len(stages.root)} stages loaded.')
    return stages

@cached('data/items-penguin-stats.json', ItemList)
def load_items() -> ItemList:
    logger.info('Loading items...')
    json_data = requests.get(API_BASE + '/items').json()
    items = ItemList.model_validate(json_data)
    logger.info(f'{len(items.root)} items loaded.')
    return items

def stage_code_id_map() -> dict[str, list[str]]:
    stages = load_stages()
    code_map = {}

    for stage in stages.root:
        stage_code = stage.code
        stage_id = stage.stageId

        if stage_code not in code_map:
            code_map[stage_code] = []

        code_map[stage_code].append(stage_id)

    return code_map

def stage_id_code_map() -> dict[str, str]:
    stages = load_stages()
    id_map = {}

    for stage in stages.root:
        stage_code = stage.code
        stage_id = stage.stageId
        id_map[stage_id] = stage_code

    return id_map

def item_map() -> dict[str, Item]:
    items = load_items()
    return {
        item.itemId: item
        for item in items.root
    }

def convert_stage_codes(stage_codes: list[str]) -> list[str]:
    code_id_map = stage_code_id_map()
    stage_ids = []

    for code in stage_codes:
        if code not in code_id_map:
            logger.warning(f'Stage {code} not found, skipping')
            continue

        ids = code_id_map[code]
        stage_ids.extend(ids)

        if len(ids) > 1:
            logger.info(f'Stage {code} has ambiguous ids {ids}, adding both')

    return stage_ids

def get_drops(stage_ids: list[str]) -> DropSummary:
    assert len(stage_ids) > 0

    logger.info('Loading stage drops matrix...')
    url = API_BASE + '/result/matrix'
    params = {
        'server': SERVER,
        'stageFilter': ','.join(stage_ids),
        'show_closed_zones': True,
    }
    json_data = requests.get(url, params=params).json()
    drop_matrix = DropMatrix.model_validate(json_data)
    logger.info(f'{len(drop_matrix.matrix)} eles loaded.')

    drop_summary = DropSummary({})
    for drop in drop_matrix.matrix:
        stage_id = drop.stageId

        if stage_id not in drop_summary.root:
            json_data = requests.get(API_BASE + '/stages/' + stage_id).json()
            stage = Stage.model_validate(json_data)
            drop_summary.root[stage_id] = StageDrops(id=stage_id,
                                                     sanity=stage.apCost,
                                                     drops=[])

        drop_rate = DropRate(id=drop.itemId,
                             rate=drop.quantity / drop.times,
                             start=drop.start,
                             end=drop.end)
        drop_summary.root[stage_id].drops.append(drop_rate)

    return drop_summary

def get_farming_plan(owned: dict[str, int],
                     required: dict[str, int],
                     exclude: list[str] = []) -> FarmingPlan:
    payload = {
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
    json_data = requests.post(PLANNER_URL, json=payload).json()
    farming_plan = FarmingPlan.model_validate(json_data)
    logger.info(f'{len(farming_plan.stages)} stages, {len(farming_plan.syntheses)} syntheses loaded')
    return farming_plan

if __name__ == '__main__':
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    load_stages()
    load_items()
    stage_code_id_map()
    stage_id_code_map()
