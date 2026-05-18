import requests
import json

from utils import cached

SERVER = 'CN'
API_BASE = 'https://penguin-stats.io/PenguinStats/api/v2'

@cached('data/stages.json')
def load_stages():
    print('Loading stages...')
    stages = requests.get(API_BASE + '/stages').json()
    return stages

@cached('data/stage-code-map.json')
def stage_code_map():
    stages = load_stages()
    code_map = {}

    for stage in stages:
        stage_code = stage['code']
        stage_id = stage['stageId']

        if stage_code not in code_map:
            code_map[stage_code] = []

        code_map[stage_code].append(stage_id)

    return code_map

@cached('data/stage-id-map.json')
def stage_id_map():
    stages = load_stages()
    id_map = {}

    for stage in stages:
        stage_code = stage['code']
        stage_id = stage['stageId']
        id_map[stage_id] = stage_code

    return id_map

@cached('data/items-penguin-stats.json')
def load_items():
    print('Loading item IDs...')
    items_list = requests.get(API_BASE + '/items').json()
    print(len(items_list), 'eles loaded.')

    return {
        item['itemId']: {
            'name': item['name_i18n']['en'],
            'rarity': item['rarity'],
            'type': item['itemType'],
        }
        for item in items_list
        if 'en' in item['name_i18n']
    }

def convert_stage_codes(stage_codes, ):
    id_map = stage_id_map()
    code_map = stage_code_map()

    stage_ids = []

    for code in stage_codes:
        if code not in code_map:
            print(f'Stage {code} not found, skipping')
            continue

        ids = code_map[code]
        stage_ids.extend(ids)

        if len(ids) > 1:
            print(f'Stage {code} has ambiguous ids {ids}, adding both')

    return stage_ids


def load_drops(stage_ids, ):
    assert len(stage_ids) > 0
    print('Loading stage drops matrix...')
    drops_matrix = requests.get(API_BASE + '/result/matrix',
                                params={
                                    'server': SERVER,
                                    'stageFilter': ','.join(stage_ids),
                                    'show_closed_zones': True,
                                }).json()
    print(len(drops_matrix['matrix']), 'eles loaded.')

    stage_drops = {}
    for drop in drops_matrix['matrix']:
        stage_id = drop['stageId']

        if stage_id not in stage_drops:
            stage_info = requests.get(API_BASE + '/stages/' + stage_id).json()
            stage_drops[stage_id] = {
                'stageId': stage_id,
                'sanity': stage_info['apCost'],
                'drops': [],
            }

        stage_drops[stage_id]['drops'].append({
            'id': drop['itemId'],
            'rate': drop['quantity'] / drop['times'],
            'start': drop['start'],
            'end': drop['end'],
        })

    return stage_drops

def farming_plan(owned, required, exclude=[]):
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

    url = 'https://planner.penguin-stats.io/plan'
    resp = requests.post(url, json=payload).json()

    stages = [
        {
            'stage_id': stage['stageId'],
            'count': stage['count'],
        }
        for stage in resp['stages']
    ]

    syntheses = [
        {
            'target': synthesis['target'],
            'count': synthesis['count'],
        }
        for synthesis in resp['syntheses']
    ]

    return {
        'sanity': resp['cost'],
        'stages': stages,
        'syntheses': syntheses,
    }

if __name__ == '__main__':
    id_map = load_items()
    reserves_path = 'data/reserves.json'
    output_path = 'data/output.json'
    output = []

    with open(reserves_path, 'r') as file:
        data = json.load(file)

    key = lambda x: x['rarity']
    output = sorted(data, key=key)

#    items = data
#    for item in items:
#        have = item.get('have', 0)
#        need = item.get('need', 0)
#        item['have'] = have
#        item['need'] = need
#        item['name'] = id_map[item['id']]['name']
#        item['rarity'] = id_map[item['id']]['rarity']
#        output.append(item)

    with open(output_path, 'w') as file:
        json.dump(output, file, indent=2)
