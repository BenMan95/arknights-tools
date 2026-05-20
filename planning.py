import argparse
import json
from models.penguin_stats import PlannerConfig, Item, FarmingPlan
from penguin_stats import get_farming_plan, get_stage_map, get_item_map
from efficiency import calc_stages_efficiency
from typing import Any

import logging
logger = logging.getLogger(__name__)

def main():
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--threshold', type=float, default=0.99)
    args = parser.parse_args()

    data_str: str = input()
    json_data: dict[str, Any] = json.loads(data_str)
    planner_config: PlannerConfig = PlannerConfig.model_validate(json_data)

    item_map: dict[str, Item] = get_item_map()
    owned: dict[str, int] = {}
    required: dict[str, int] = {}
    for item_goal in planner_config.items:
        if item_goal.id not in item_map:
            logger.info(f'Item ID {item_goal.id} not found, skipping.')
            continue
        if item_map[item_goal.id].itemType != 'MATERIAL':
            continue
        owned[item_goal.id] = item_goal.have
        required[item_goal.id] = item_goal.need

    exclusions: list[str] = []
    efficiency_dict: dict[str, float] = {}
    attempts: int = 0
    plan: FarmingPlan | None = None
    while True:
        attempts += 1
        logger.info(f'Attempt {attempts}...')
        plan = get_farming_plan(owned, required, exclusions)

        stage_ids: list[str] = [ stage.stageId for stage in plan.stages ]
        new_stage_ids: list[str] = [
            stage_id for stage_id in stage_ids
            if stage_id not in efficiency_dict
        ]

        new_efficiency_dict: dict[str, float] = calc_stages_efficiency(new_stage_ids)
        for stage_id, efficiency in new_efficiency_dict.items():
            efficiency_dict[stage_id] = efficiency

        new_exclusions: list[str] = [
            stage_id for stage_id in new_stage_ids
            if efficiency_dict[stage_id] < args.threshold
        ]

        if not new_exclusions:
            break

        exclusions.extend(new_exclusions)
        are_is: str = 'are' if len(new_exclusions) > 1 else 'is'
        logger.info(f'{','.join(new_exclusions)} {are_is} inefficient, retrying.')

    print('=' * 25, 'PLAN', '=' * 25)

    stage_map = get_stage_map()
    sanity: int = plan.cost
    print(f'Farming: {sanity} sanity')
    for battle in plan.stages:
        stage_id: str = battle.stageId
        efficiency: float = efficiency_dict[stage_id]
        stage_code: str = stage_map[stage_id].code
        count: int = battle.count
        print(f'{stage_id} ({stage_code}) x {count}: {efficiency:.5f}')

    print()

    print('Crafting:')
    for synthesis in plan.syntheses:
        item_id: str = synthesis.target
        item_name: str = item_map[item_id].name_i18n.en
        count: int = synthesis.count
        print(f'{item_name} x {count}')

if __name__ == '__main__':
    main()