from typing import assert_type
import argparse
import json
from models.penguin_stats import PlannerConfig, FarmingPlan
from penguin_stats import get_farming_plan, get_stage_map, get_item_map
from efficiency import calc_stages_efficiency

import logging
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--threshold', type=float, default=0.99)
    args = parser.parse_args()

    data_str = input()
    json_data = json.loads(data_str)
    planner_config = PlannerConfig.model_validate(json_data)

    get_item_map = get_item_map()
    owned = {}
    required = {}
    for item_goal in planner_config.items:
        if item_goal.id not in get_item_map:
            logger.info(f'Item ID {item_goal.id} not found, skipping.')
            continue
        if get_item_map[item_goal.id].itemType != 'MATERIAL':
            continue
        owned[item_goal.id] = item_goal.have
        required[item_goal.id] = item_goal.need

    exclusions = []
    efficiency_dict = {}
    attempts = 0
    plan = None
    while True:
        attempts += 1
        logger.info(f'Attempt {attempts}...')
        plan = get_farming_plan(owned, required, exclusions)

        stage_ids = [ stage.stageId for stage in plan.stages ]
        new_stage_ids = [
            stage_id for stage_id in stage_ids
            if stage_id not in efficiency_dict
        ]

        new_efficiency_dict = calc_stages_efficiency(new_stage_ids)
        for stage_id, efficiency in new_efficiency_dict.items():
            efficiency_dict[stage_id] = efficiency

        new_exclusions = [
            stage_id for stage_id in new_stage_ids
            if efficiency_dict[stage_id] < args.threshold
        ]
        exclusions.extend(new_exclusions)
        if not new_exclusions:
            break
        logger.info(f'{','.join(new_exclusions)} are inefficient, retrying.')

    print('=' * 25, 'PLAN', '=' * 25)

    get_stage_map = get_stage_map()
    sanity = plan.cost
    print(f'Farming: {sanity} sanity')
    for battle in plan.stages:
        stage_id = battle.stageId
        efficiency = efficiency_dict[stage_id]
        stage_code = get_stage_map[stage_id].stageId
        count = battle.count
        print(f'{stage_id} ({stage_code}) x {count}: {efficiency:.5f}')

    print()

    print('Crafting:')
    for synthesis in plan.syntheses:
        item_id = synthesis.target
        item_name = get_item_map[item_id].name_i18n.en
        count = synthesis.count
        print(f'{item_name} x {count}')
