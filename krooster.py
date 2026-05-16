import requests
from utils import cached

OPERATOR_DATA_URL = 'https://raw.githubusercontent.com/neeia/ak-roster/refs/heads/main/src/data/operators.json'
ITEM_DATA_URL = 'https://raw.githubusercontent.com/neeia/ak-roster/refs/heads/main/src/data/items.json'

@cached('data/operators.json')
def get_operator_data(read_cache=True):
    print('Loading operator data...')
    data = requests.get(OPERATOR_DATA_URL).json()
    return data

@cached('data/items-krooster.json')
def get_item_data(read_cache=True):
    print('Loading item data...')
    data = requests.get(ITEM_DATA_URL).json()
    return data

