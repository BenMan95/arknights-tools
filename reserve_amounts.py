import argparse
import json
from typing import Callable

from utils import cached
from krooster import get_operator_data, get_item_data
from models.krooster import OperatorDict, ItemDict, Ingredient

SHOP_ITEMS = ['30073', '30083', '30093']
BIG_NUMBER = 999

def _update_dict(old: dict[str, int],
                 new: dict[str, int],
                 func: Callable[[int, int], int]) -> None:
    for key, value in new.items():
        old_val: int = old.get(key, 0)
        old[key] = func(old_val, value)

def _to_dict(mats: list[Ingredient]) -> dict[str, int]:
    return {
        mat.id: mat.quantity
        for mat in mats
    }

@cached('data/reserve.json')
def calc_reserve_amounts() -> dict[str, int]:
    operator_data: OperatorDict = get_operator_data()

    operator_max: dict[str, int] = {}
    elite_max: dict[str, int] = {}
    skill_max: dict[str, int] = {}
    mastery_max: dict[str, int] = {}
    module_max: dict[str, int] = {}

    add: Callable[[int, int], int] = lambda a,b:a+b
    for operator in operator_data.root.values():
        if operator.isCnOnly:
            continue

        elite_mats: dict[str, int] = {}
        for elite_lvl in operator.eliteLevels:
            ingredients: dict[str, int] = _to_dict(elite_lvl.ingredients)
            _update_dict(elite_mats, ingredients, add)
        _update_dict(elite_max, elite_mats, max)

        skill_mats: dict[str, int] = {}
        for skill_lvl in operator.skillLevels:
            ingredients: dict[str, int] = _to_dict(skill_lvl.ingredients)
            _update_dict(skill_mats, ingredients, add)
        _update_dict(skill_max, skill_mats, max)

        operator_mastery_max: dict[str, int] = {}
        for skill in operator.skillData:
            mastery_mats: dict[str, int] = {}
            for mastery in skill.masteries:
                ingredients: dict[str, int] = _to_dict(mastery.ingredients)
                _update_dict(mastery_mats, ingredients, add)
            _update_dict(mastery_max, mastery_mats, max)
            _update_dict(operator_mastery_max, mastery_mats, max)

        operator_module_max: dict[str, int] = {}
        for module in operator.moduleData:
            module_mats: dict[str, int] = {}
            for mod_stage in module.stages:
                ingredients: dict[str, int] = _to_dict(mod_stage.ingredients)
                _update_dict(module_mats, ingredients, add)
            _update_dict(module_max, module_mats, max)
            _update_dict(operator_module_max, module_mats, max)

        operator_mats: dict[str, int] = {}
        _update_dict(operator_mats, elite_mats, add)
        _update_dict(operator_mats, skill_mats, add)
        _update_dict(operator_mats, operator_mastery_max, add)
        _update_dict(operator_mats, operator_module_max, add)
        _update_dict(operator_max, operator_mats, max)

    return operator_max

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', '--add', action='store_true')
    group.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('-s', '--shop', action='store_true')
    args = parser.parse_args()

    reserve_amounts: dict[str, int] = calc_reserve_amounts()
    item_data: ItemDict = get_item_data()

    if args.add or args.overwrite or args.shop:
        data_str: str = input()
        data = json.loads(data_str)
        for item in data['items']:
            item_id: str = item['id']
            if args.shop and item_id in SHOP_ITEMS:
                item['have'] = BIG_NUMBER
            if args.add:
                item['need'] += reserve_amounts.get(item_id, 0)
            if args.overwrite:
                item['need'] = reserve_amounts.get(item_id, 0)
        print(json.dumps(data))
    else:
        for item_id, qty in reserve_amounts.items():
            if item_id in item_data.root:
                name: str = item_data.root[item_id].name
                rarity: int = item_data.root[item_id].tier
                print(f'{item_id} - {name} ({rarity}): {qty}')
            else:
                print(f'{item_id}: {qty}')

if __name__ == '__main__':
    main()
