import argparse
import json
import requests
from penguin_stats import farming_plan, stage_id_map, load_items
from reserve_amounts import calc_reserve_amounts
from efficiency import calc_stages_efficiency

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--threshold', type=float, default=0.95)
    args = parser.parse_args()

    data_str = input()
    data = json.loads(data_str)

    item_map = load_items()
    owned = {}
    required = {}
    for item in data['items']:
        if item['id'] not in item_map:
            continue
        if item_map[item['id']]['type'] != 'MATERIAL':
            continue
        owned[item['id']] = item['have']
        required[item['id']] = item['need']

    exclude = []
    efficiency_dict = {}
    attempts = 0
    done = False
    while not done:
        print()
        attempts += 1
        print('Attempt', attempts)
        print('Loading plan...')
        plan = farming_plan(owned, required, exclude)

        stage_ids = [
            stage['stage_id']
            for stage in plan['stages']
        ]
        new_stage_ids = [
            stage_id for stage_id in stage_ids
            if stage_id not in efficiency_dict
        ]

        efficiency_values = calc_stages_efficiency(new_stage_ids)
        for stage in efficiency_values:
            efficiency_dict[stage['stage_id']] = stage['efficiency']

        done = True
        for stage_id in stage_ids:
            efficiency = efficiency_dict[stage_id]
            if efficiency < args.threshold:
                done = False
                exclude.append(stage_id)

        if not done:
            print('Retrying without:', ','.join(exclude))

    print()
    print('=' * 25, 'PLAN', '=' * 25)
    print()

    id_map = stage_id_map()
    sanity = plan['sanity']
    print(f'Farming: {sanity} sanity')
    for stage in plan['stages']:
        stage_id = stage['stage_id']
        efficiency = efficiency_dict[stage_id]
        stage_code = id_map[stage_id]
        count = stage['count']
        print(f'{stage_id} ({stage_code}) x {count}: {efficiency:.5f}')

    print()

    print('Crafting:')
    for synthesis in plan['syntheses']:
        item_id = synthesis['target']
        item_name = item_map[item_id]['name']
        count = synthesis['count']
        print(f'{item_name} x {count}')
