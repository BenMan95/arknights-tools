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
    data = requests.get(OPERATOR_DATA_URL).json()
    return OperatorDict.model_validate(data)

@cached('data/items-krooster.json', ItemDict)
def get_item_data() -> ItemDict:
    logger.info('Loading item data...')
    data = requests.get(ITEM_DATA_URL).json()
    return ItemDict.model_validate(data)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    operators = get_operator_data()
    print(f'{len(operators.root)} operators loaded')
    items = get_item_data()
    print(f'{len(items.root)} items loaded')
