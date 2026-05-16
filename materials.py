from sanity_values import load_values_peteryr as load_sanity_values

materials = """
Tactical Battle Record,215
LMD,345200
Polymerized Gel,8
Polyester,3
Sugar,4
Oriron Cluster,15
Chip Catalyst,3
Specialist Chip Pack,6
Specialist Chip,4
""".strip()

sanity_dict = load_sanity_values()
sanity_dict['Chip Catalyst'] = 122.4

sanity = 0
for line in materials.split('\n'):
    material, amount = line.split(',')
    amount = int(amount)

    if material in sanity_dict:
        sanity += sanity_dict[material] * amount
    else:
        print('Skipping', material)

print(sanity)
