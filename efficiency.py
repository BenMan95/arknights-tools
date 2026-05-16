import argparse
import time
import numpy as np
import pandas as pd

from sanity_values import load_values_moe, load_values_peteryr
from penguin_stats import load_items, load_drops, stage_id_map, convert_stage_codes, stage_id_map

LMD_RATE = 12

def calc_material_value(stage_data, items_dict, values_dict, logging=False):
    material_value = 0
    for drop in stage_data['drops']:
        drop_name = items_dict[drop['id']]['name']

        start = drop.get('start')
        end = drop.get('end')
        cur = time.time() * 1000

        if start and start > cur:
            if logging:
                print(f'{stage_id}: {drop_name} skipped (Not started)')
            continue

        if end and end < cur:
            if logging:
                print(f'{stage_id}: {drop_name} skipped (Ended)')
            continue

        if drop_name not in values_dict:
            if logging:
                print(f'{stage_id}: {drop_name} skipped (Unknown sanity value)')
            continue

        material_value += drop['rate'] * values_dict[drop_name]

    if material_value == 0:
        print(f'{stage_id}: no drops, skipped')
        return None

    material_value += LMD_RATE * stage_data['sanity'] * values_dict['LMD']
    return material_value


def calc_stages_efficiency(stage_ids, logging=False):
    items_dict = load_items()
    stage_drops = load_drops(stage_ids)
    values_dict = load_values_peteryr()

    if logging:
        print('Processing data...')

    results = []
    for stage_id in stage_drops:
        data = stage_drops[stage_id]
        material_value = calc_material_value(data,
                                             items_dict,
                                             values_dict,
                                             logging=logging)
        results.append({
            'stage_id': stage_id,
            'efficiency': material_value / data['sanity'],
        })

    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--codes', action='extend', nargs='*', default=[])
    parser.add_argument('-i', '--ids', action='extend', nargs='*', default=[])
    args = parser.parse_args()

    stage_ids = args.ids + convert_stage_codes(args.codes)
    results = calc_stages_efficiency(stage_ids, logging=False)
    id_map = stage_id_map()

    print()
    print('='*25, 'RESULTS', '='*25)

    key = lambda x: -x['efficiency']
    sorted_results = sorted(results, key=key)
    for result in sorted_results:
        stage_id = result['stage_id']
        stage_code = id_map[stage_id]
        efficiency = result['efficiency']
        print(f'{stage_id} ({stage_code}): {efficiency:.06f}')

