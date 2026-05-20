import requests

from utils import cached
from models.krooster import OperatorDict, ItemDict

import logging
logger = logging.getLogger(__name__)

OPERATOR_DATA_URL = 'https://raw.githubusercontent.com/neeia/ak-roster/refs/heads/main/src/data/operators.json'
ITEM_DATA_URL = 'https://raw.githubusercontent.com/neeia/ak-roster/refs/heads/main/src/data/items.json'

@cached('data/operators.json', OperatorDict)
def get_operator_data() -> OperatorDict:
    logger.info('Loading operator data...')
    json_data = requests.get(OPERATOR_DATA_URL).json()
    return OperatorDict.model_validate(json_data)

@cached('data/items-krooster.json', ItemDict)
def get_item_data() -> ItemDict:
    logger.info('Loading item data...')
    json_data = requests.get(ITEM_DATA_URL).json()
    return ItemDict.model_validate(json_data)

if __name__ == '__main__':
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    operators = get_operator_data()
    logger.info(f'{len(operators.root)} operators loaded')

    items = get_item_data()
    logger.info(f'{len(items.root)} items loaded')
