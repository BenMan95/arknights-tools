import logging

from sanity_values import load_values_peteryr

logger = logging.getLogger(__name__)

def calculate_total_value(materials: list[tuple[str, float]]) -> float:
    sanity_dict: dict[str, float] = load_values_peteryr()

    sanity: float = 0
    for material, amount in materials:
        if material in sanity_dict:
            logger.info(f'{material} has unknown sanity value, skipping')
        else:
            sanity += sanity_dict[material] * amount
    return sanity

def main():
    data_str = input().strip()

    materials: list[tuple[str, float]] = []
    for line in data_str.split('\n'):
        material, amount = line.split(',')
        amount = float(amount)
        materials.append((material, amount))

    sanity: float = calculate_total_value(materials)
    print(sanity)

if __name__ == '__main__':
    main()