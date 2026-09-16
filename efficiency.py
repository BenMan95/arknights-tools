import argparse
import itertools
import logging
import re
import time
from collections.abc import Callable

from models.custom import StageEfficiency
from models.penguin_stats import DropMatrix, Item, Stage
from penguin_stats import (
    convert_stage_codes,
    get_drop_matrix,
    get_item_map,
    get_stage_map,
)
from sanity_values import load_values_peteryr

logger = logging.getLogger(__name__)

LMD_RATE: int = 12


def expand_codes(codes: list[str]):
    output: list[str] = []

    pattern = r'(\d+)\*(\d+)'
    for code in codes:
        matches: list[tuple[str, str]] = re.findall(pattern, code)

        ranges = [range(int(start), int(end) + 1) for start, end in matches]

        for values in itertools.product(*ranges):
            iterator = iter(values)
            subbed = re.sub(pattern, lambda _: str(next(iterator)), code)  # noqa: B023
            output.append(subbed)

    return output


def calc_stages_efficiency(
    stage_ids: list[str], timed: bool = True
) -> dict[str, StageEfficiency]:
    if len(stage_ids) == 0:
        logger.info('No stage IDs given, returning blank results...')
        return {}

    now: float = time.time() * 1000
    item_dict: dict[str, Item] = get_item_map()
    drop_matrix: DropMatrix = get_drop_matrix(stage_ids)
    value_dict: dict[str, float] = load_values_peteryr()
    stage_map: dict[str, Stage] = get_stage_map()

    logger.info('Processing data...')

    lmd_efficiency: float = LMD_RATE * value_dict['LMD']
    stage_efficiency_values: dict[str, StageEfficiency] = {}
    for drop in drop_matrix.matrix:
        drop_name: str = item_dict[drop.itemId].name_i18n.en
        stage_id: str = drop.stageId

        if timed and drop.start and drop.start > now:
            logger.info(f'{stage_id}: {drop_name} skipped (Not started)')
            continue

        if timed and drop.end and drop.end < now:
            logger.info(f'{stage_id}: {drop_name} skipped (Ended)')
            continue

        if drop_name not in value_dict:
            logger.info(f'{stage_id}: {drop_name} skipped (Unknown sanity value)')
            continue

        drop_value: float = value_dict[drop_name] * drop.quantity / drop.times
        drop_efficiency: float = drop_value / stage_map[stage_id].apCost

        if stage_id in stage_efficiency_values:
            stage_efficiency: StageEfficiency = stage_efficiency_values[stage_id]
            stage_efficiency.efficiency += drop_efficiency

            if drop_efficiency > stage_efficiency.main_drop_efficiency:
                stage_efficiency.main_drop = drop_name
                stage_efficiency.main_drop_efficiency = drop_efficiency

        else:
            stage_efficiency_values[stage_id] = StageEfficiency(
                efficiency=lmd_efficiency + drop_efficiency,
                main_drop=drop_name,
                main_drop_efficiency=drop_efficiency,
            )

    # stage_sanity_values: dict[str, float] = defaultdict(float)
    # for drop in drop_matrix.matrix:
    #     drop_name: str = item_dict[drop.itemId].name_i18n.en

    #     if timed and drop.start and drop.start > now:
    #         logger.info(f'{drop.stageId}: {drop_name} skipped (Not started)')
    #         continue

    #     if timed and drop.end and drop.end < now:
    #         logger.info(f'{drop.stageId}: {drop_name} skipped (Ended)')
    #         continue

    #     if drop_name not in value_dict:
    #         logger.info(f'{drop.stageId}: {drop_name} skipped (Unknown sanity value)')
    #         continue

    #     drop_value: float = value_dict[drop_name] * drop.quantity / drop.times
    #     stage_sanity_values[drop.stageId] += drop_value

    # stage_efficiency_values: dict[str, StageEfficiency] = {}
    # lmd_efficiency: float = LMD_RATE * value_dict['LMD']
    # for stage_id, sanity_value in stage_sanity_values.items():
    #     if not sanity_value:
    #         logger.info(f'{stage_id}: no drops, skipped')
    #         continue
    #     efficiency: float = lmd_efficiency + sanity_value / stage_map[stage_id].apCost
    #     stage_efficiency_values[stage_id] = efficiency

    # for id in stage_ids:
    #     if id not in stage_efficiency_values:
    #         logger.info(f'No results for {id}')

    return stage_efficiency_values


def main():
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--untimed', action='store_false', dest='timed')
    parser.add_argument('-c', '--codes', action='extend', nargs='*', default=[])
    parser.add_argument('-i', '--ids', action='extend', nargs='*', default=[])
    args = parser.parse_args()

    expanded_codes = convert_stage_codes(expand_codes(args.codes))
    stage_ids: list[str] = expand_codes(args.ids) + expanded_codes
    results: dict[str, StageEfficiency] = calc_stages_efficiency(stage_ids, args.timed)
    stage_map: dict[str, Stage] = get_stage_map()

    print()
    print('=' * 25, 'RESULTS', '=' * 25)

    key: Callable[[tuple[str, StageEfficiency]], float] = lambda x: -x[1].efficiency
    sorted_results: list[tuple[str, StageEfficiency]] = sorted(results.items(), key=key)
    for stage_id, stage_efficiency in sorted_results:
        stage_code: str = stage_map[stage_id].code
        efficiency = stage_efficiency.efficiency
        main_drop = stage_efficiency.main_drop
        main_drop_efficiency = stage_efficiency.main_drop_efficiency
        print(f'{stage_id} ({stage_code}): {efficiency:.06f} ({main_drop}: {main_drop_efficiency:.06f})')


if __name__ == '__main__':
    main()
