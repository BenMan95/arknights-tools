import argparse
import requests
import json

from krooster import *
from utils import cached

SHOP_ITEMS = ['30073', '30083', '30093']
BIG_NUMBER = 999

def update_dict(old, new, func):
    for key, value in new.items():
        old_val = old.get(key, 0)
        old[key] = func(old_val, value)

def convert_mats(mats):
    return {
        mat['id']: mat['quantity']
        for mat in mats
    }

@cached('data/reserve.json')
def calc_reserve_amounts():
    operator_data = get_operator_data()

    operator_max = {}
    elite_max = {}
    skill_max = {}
    mastery_max = {}
    module_max = {}

    add = lambda a,b:a+b
    for operator in operator_data.values():
        if operator['isCnOnly']:
            continue

        elite_mats = {}
        for elite_lvl in operator['eliteLevels']:
            mats = convert_mats(elite_lvl['ingredients'])
            update_dict(elite_mats, mats, add)
        update_dict(elite_max, elite_mats, max)

        skill_mats = {}
        for skill_lvl in operator['skillLevels']:
            mats = convert_mats(skill_lvl['ingredients'])
            update_dict(skill_mats, mats, add)
        update_dict(skill_max, skill_mats, max)

        operator_mastery_max = {}
        for skill in operator['skillData']:
            mastery_mats = {}
            for mastery in skill['masteries']:
                mats = convert_mats(mastery['ingredients'])
                update_dict(mastery_mats, mats, add)
            update_dict(mastery_max, mastery_mats, max)
            update_dict(operator_mastery_max, mastery_mats, max)

        operator_module_max = {}
        for module in operator['moduleData']:
            module_mats = {}
            for mod_stage in module['stages']:
                mats = convert_mats(mod_stage['ingredients'])
                update_dict(module_mats, mats, add)
            update_dict(module_max, module_mats, max)
            update_dict(operator_module_max, module_mats, max)

        operator_mats = {}
        update_dict(operator_mats, elite_mats, add)
        update_dict(operator_mats, skill_mats, add)
        update_dict(operator_mats, operator_mastery_max, add)
        update_dict(operator_mats, operator_module_max, add)
        update_dict(operator_max, operator_mats, max)

    return operator_max

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', '--add', action='store_true')
    group.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('-s', '--shop', action='store_true')
    args = parser.parse_args()

    reserve_amounts = calc_reserve_amounts()
    items_dict = get_item_data()

    if args.add or args.overwrite or args.shop:
        data_str = input()
        data = json.loads(data_str)
        for item in data['items']:
            item_id = item['id']
            if item_id not in reserve_amounts:
                continue
            if args.shop and item_id in SHOP_ITEMS:
                item['have'] = BIG_NUMBER
            if args.add:
                item['need'] += reserve_amounts[item_id]
            if args.overwrite:
                item['need'] = reserve_amounts[item_id]
        print(json.dumps(data))
    else:
        for item_id, qty in reserve_amounts.items():
            if item_id in items_dict:
                name = items_dict[item_id]['name']
                rarity = items_dict[item_id]['tier']
                print(f'{item_id} - {name} ({rarity}): {qty}')
            else:
                print(f'{item_id}: {qty}')

