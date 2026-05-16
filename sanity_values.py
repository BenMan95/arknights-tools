from utils import cached

import json
from urllib.parse import quote
import numpy as np
import pandas as pd

MOE_SPREADSHEET_ID = '12X0uBQaN7MuuMWWDTiUjIni_MOP015GnulggmBJgBaQ'
MOE_SHEET_NAME = quote('Expected Sanity Per Material')
MOE_URL = f'https://docs.google.com/spreadsheets/d/{MOE_SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={MOE_SHEET_NAME}'

PETERYR_SPREADSHEET_ID = '1RRiTIYVUNUf-xW8ljAJdYEOuSo23lpjHkPa0-zuC_4k'
PETERYR_SHEET_GID = '253510834'
PETERYR_URL = f'https://docs.google.com/spreadsheets/d/{PETERYR_SPREADSHEET_ID}/export?format=csv&gid={PETERYR_SHEET_GID}'

type SanityValues = dict[str, float]

@cached('data/values_moe.json')
def load_values_moe(read_cache=True):
    print("Loading Moe's sanity values...")
    sheet = pd.read_csv(MOE_URL, header=None).to_numpy()

    grouped_materials = [
        sheet[4:10, [2,5]],
        sheet[4:10, [8,12]],
        sheet[4:22, [15,18]],
        sheet[4:22, [21,23]],
        sheet[4:9, [26,28]],
        sheet[16:32, [2,5]],
    ]

    materials = np.concatenate(grouped_materials)
    print(len(materials), 'eles loaded.')

    out = {
        name: sanity
        for name, sanity
        in materials
    }

    return out

@cached('data/values_moe.json')
def load_values_peteryr(read_cache=True):
    print("Loading PeterYR's sanity values...")
    sheet = pd.read_csv(PETERYR_URL, header=None).to_numpy()
    materials = sheet[[2,0], 7:].transpose()
    print(len(materials), 'eles loaded.')

    return {
        name: float(sanity)
        for name, sanity
        in materials
    }

def _load_values_combined(read_cache=True):
    values_moe = load_values_moe(read_cache=read_cache)
    values_peteryr = load_values_peteryr(read_cache=read_cache)
    values_combined = {}

    for key,value in values_moe.items():
        key = key.replace('Skill Summary', 'Skill Summary -')
        values_combined[key] = { "moe": value }

    for key,value in values_peteryr.items():
        if 'Chip Pack' in key:
            key = 'Chip Pack'
        elif 'Chip' in key:
            key = 'Chips'

        if key not in values_combined:
            values_combined[key] = {}
        values_combined[key]["peteryr"] = value

    return values_combined

def _disp_table(values):
    rows = [
        [key,str(value.get('moe','')),str(value.get('peteryr',''))]
        for key,value
        in values.items()
    ]
    rows.insert(0, ['name','moe','peteryr'])

    cols = zip(*rows)
    widths = [
        max(map(len,col))
        for col in cols
    ]
    dividers = ['-'*w for w in widths]
    divider_str = '+' + '+'.join(dividers) + '+'

    print(divider_str)
    for i,row in enumerate(rows):
        padded_vals = [
            value.ljust(width)
            for value,width
            in zip(row,widths)
        ]

        print('|' + '|'.join(padded_vals) + '|')
        if i == 0:
            print(divider_str)
    print(divider_str)

if __name__ == '__main__':
    values = _load_values_combined(read_cache=False)
    _disp_table(values)
