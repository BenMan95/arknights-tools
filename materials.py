from sanity_values import load_values_peteryr

import logging
logger = logging.getLogger(__name__)

def calculate_total_value(materials: list[tuple[str, float]]):
    sanity_dict = load_values_peteryr()
    sanity_dict['Chip Catalyst'] = 122.4

    sanity = 0
    for material, amount in materials:
        if material not in sanity_dict:
            logger.info(f'{material} has unknown sanity value, skipping')
            continue
        sanity += sanity_dict[material] * amount
    return sanity

if __name__ == '__main__':
    data_str = input().strip()

    materials = []
    for line in data_str.split('\n'):
        material, amount = line.split(',')
        amount = float(amount)
        materials.append([material, amount])

    sanity = calculate_total_value(materials)
    print(sanity)