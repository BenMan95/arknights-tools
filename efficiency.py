import argparse
import time

from sanity_values import load_values_peteryr
from typing import Callable
from penguin_stats import get_item_map, get_drop_matrix, convert_stage_codes, get_stage_map
from models.penguin_stats import Item, DropMatrix, Stage

import logging
logger = logging.getLogger(__name__)

LMD_RATE: int = 12

def calc_stages_efficiency(stage_ids: list[str]) -> dict[str, float]:
    now: float = time.time() * 1000
    item_dict: dict[str, Item] = get_item_map()
    drop_matrix: DropMatrix = get_drop_matrix(stage_ids)
    value_dict: dict[str, float] = load_values_peteryr()
    stage_map: dict[str, Stage] = get_stage_map()

    logger.info('Processing data...')

    stage_sanity_values: dict[str, float] = {}
    for drop in drop_matrix.matrix:
        if drop.stageId not in stage_sanity_values:
            stage_sanity_values[drop.stageId] = 0

        drop_name: str = item_dict[drop.itemId].name_i18n.en

        if drop.start and drop.start > now:
            logger.info(f'{drop.stageId}: {drop_name} skipped (Not started)')
            continue

        if drop.end and drop.end < now:
            logger.info(f'{drop.stageId}: {drop_name} skipped (Ended)')
            continue

        if drop_name not in value_dict:
            logger.info(f'{drop.stageId}: {drop_name} skipped (Unknown sanity value)')
            continue

        drop_value: float = value_dict[drop_name] * drop.quantity / drop.times
        stage_sanity_values[drop.stageId] += drop_value

    stage_efficiency_values: dict[str, float] = {}
    lmd_efficiency: float = LMD_RATE * value_dict['LMD']
    for stage_id, sanity_value in stage_sanity_values.items():
        if not sanity_value:
            logger.info(f'{stage_id}: no drops, skipped')
            continue
        efficiency: float = lmd_efficiency + sanity_value/stage_map[stage_id].apCost
        stage_efficiency_values[stage_id] = efficiency

    return stage_efficiency_values

def main():
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--codes', action='extend', nargs='*', default=[])
    parser.add_argument('-i', '--ids', action='extend', nargs='*', default=[])
    args = parser.parse_args()

    stage_ids: list[str] = args.ids + convert_stage_codes(args.codes)
    results: dict[str, float] = calc_stages_efficiency(stage_ids)
    stage_map: dict[str, Stage] = get_stage_map()

    print()
    print('='*25, 'RESULTS', '='*25)

    key: Callable[[tuple[str, float]], float] = lambda x: -x[1]
    sorted_results: list[tuple[str, float]] = sorted(results.items(), key=key)
    for stage_id, efficiency in sorted_results:
        stage_code: str = stage_map[stage_id].code
        print(f'{stage_id} ({stage_code}): {efficiency:.06f}')

if __name__ == '__main__':
    main()
