from typing import Callable
import argparse
import json

from models.krooster import OperatorDict, ItemDict, Ingredient
from krooster import get_operator_data, get_item_data
from utils import cached

SHOP_ITEMS = ['30073', '30083', '30093']
BIG_NUMBER = 999

def _update_dict(old: dict[str, int],
                 new: dict[str, int],
                 func: Callable[[int, int], int]) -> None:
    for key, value in new.items():
        old_val = old.get(key, 0)
        old[key] = func(old_val, value)

def _ingredients_to_dict(mats: list[Ingredient]) -> dict[str, int]:
    return {
        mat.id: mat.quantity
        for mat in mats
    }

@cached('data/reserve.json')
def calc_reserve_amounts() -> dict[str, int]:
    operator_data: OperatorDict = get_operator_data()

    operator_max = {}
    elite_max = {}
    skill_max = {}
    mastery_max = {}
    module_max = {}

    add = lambda a,b:a+b
    for operator in operator_data.root.values():
        if operator.isCnOnly:
            continue

        elite_mats = {}
        for elite_lvl in operator.eliteLevels:
            ingredients = _ingredients_to_dict(elite_lvl.ingredients)
            _update_dict(elite_mats, ingredients, add)
        _update_dict(elite_max, elite_mats, max)

        skill_mats = {}
        for skill_lvl in operator.skillLevels:
            ingredients = _ingredients_to_dict(skill_lvl.ingredients)
            _update_dict(skill_mats, ingredients, add)
        _update_dict(skill_max, skill_mats, max)

        operator_mastery_max = {}
        for skill in operator.skillData:
            mastery_mats = {}
            for mastery in skill.masteries:
                ingredients = _ingredients_to_dict(mastery.ingredients)
                _update_dict(mastery_mats, ingredients, add)
            _update_dict(mastery_max, mastery_mats, max)
            _update_dict(operator_mastery_max, mastery_mats, max)

        operator_module_max = {}
        for module in operator.moduleData:
            module_mats = {}
            for mod_stage in module.stages:
                ingredients = _ingredients_to_dict(mod_stage.ingredients)
                _update_dict(module_mats, ingredients, add)
            _update_dict(module_max, module_mats, max)
            _update_dict(operator_module_max, module_mats, max)

        operator_mats = {}
        _update_dict(operator_mats, elite_mats, add)
        _update_dict(operator_mats, skill_mats, add)
        _update_dict(operator_mats, operator_mastery_max, add)
        _update_dict(operator_mats, operator_module_max, add)
        _update_dict(operator_max, operator_mats, max)

    return operator_max

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', '--add', action='store_true')
    group.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('-s', '--shop', action='store_true')
    args = parser.parse_args()

    reserve_amounts = calc_reserve_amounts()
    item_data: ItemDict = get_item_data()

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
            if item_id in item_data.root:
                name = item_data.root[item_id].name
                rarity = item_data.root[item_id].tier
                print(f'{item_id} - {name} ({rarity}): {qty}')
            else:
                print(f'{item_id}: {qty}')

