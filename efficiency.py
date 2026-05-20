import argparse
import time
import numpy as np
import pandas as pd

from sanity_values import load_values_moe, load_values_peteryr
from penguin_stats import item_map, get_drops, stage_id_code_map, convert_stage_codes, stage_id_code_map
from models.penguin_stats import Item
from models.misc import StageDrops

import logging
logger = logging.getLogger(__name__)

LMD_RATE = 12

def calc_material_value(stage_data: StageDrops,
                        item_map: dict[str, Item],
                        values_dict: dict[str, float]) -> float | None:
    material_value = 0
    for drop in stage_data.drops:
        drop_name = item_map[drop.id].name_i18n.en

        cur = time.time() * 1000
        if drop.start and drop.start > cur:
            logger.info(f'{stage_data.id}: {drop_name} skipped (Not started)')
            continue

        if drop.end and drop.end < cur:
            logger.info(f'{stage_data.id}: {drop_name} skipped (Ended)')
            continue

        if drop_name not in values_dict:
            logger.info(f'{stage_data.id}: {drop_name} skipped (Unknown sanity value)')
            continue

        material_value += drop.rate * values_dict[drop_name]

    if material_value == 0:
        logger.info(f'{stage_data.id}: no drops, skipped')
        return None

    material_value += LMD_RATE * stage_data.sanity * values_dict['LMD']
    return material_value


def calc_stages_efficiency(stage_ids: list[str]) -> dict[str, float]:
    items_dict = item_map()
    stage_drops = get_drops(stage_ids)
    values_dict = load_values_peteryr()

    logger.info('Processing data...')

    results = {}
    for stage in stage_drops.root.values():
        material_value = calc_material_value(stage, items_dict, values_dict)
        if material_value is None:
            continue
        results[stage.id] = material_value / stage.sanity

    return results

if __name__ == '__main__':
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--codes', action='extend', nargs='*', default=[])
    parser.add_argument('-i', '--ids', action='extend', nargs='*', default=[])
    args = parser.parse_args()

    stage_ids = args.ids + convert_stage_codes(args.codes)
    results = calc_stages_efficiency(stage_ids)
    id_map = stage_id_code_map()

    print()
    print('='*25, 'RESULTS', '='*25)

    key = lambda x: -x[1]
    sorted_results = sorted(results.items(), key=key)
    for stage_id, efficiency in sorted_results:
        stage_code = id_map[stage_id]
        print(f'{stage_id} ({stage_code}): {efficiency:.06f}')

