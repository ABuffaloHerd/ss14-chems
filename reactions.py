import yaml
import math
import json
from collections import deque

# Custom YAML loader to ignore unknown tags
class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    def ignore_unknown(self, node):
        return None 

SafeLoaderIgnoreUnknown.add_constructor(None, SafeLoaderIgnoreUnknown.ignore_unknown)

class ChemicalNode:
    def __init__(self, name):
        self.name = name
        self.reactants = {}  # {chemical: amount}
        self.product_amount = 0
        self.notes = []

    def __str__(self):
        return f"{self.name} : {self.reactants} makes {self.product_amount} | {self.notes}"

# Load the YAML file
with open('medicine.yml', 'r') as file:
    reactions = yaml.safe_load(file)

# Convert reactions into a dictionary for easier processing
reaction_dict = {reaction['id']: reaction for reaction in reactions}

with open('chemicals.yml', 'r') as file2:
    chem_reactions = yaml.load(file2, Loader=SafeLoaderIgnoreUnknown)

chem_dict = {reaction['id']: reaction for reaction in chem_reactions}

reaction_dict.update(chem_dict)

###########################################################################

# Create nodes for each chemical
nodes = {}
for reaction in reaction_dict.values():
    for reactant in reaction['reactants']:
        if reactant not in nodes:
            nodes[reactant] = ChemicalNode(reactant)


    for product in reaction.get('products', {}):
        if product not in nodes:
            nodes[product] = ChemicalNode(product)
        nodes[product].product_amount = reaction['products'][product]

# Add reactant relationships
for reaction in reaction_dict.values():
    for product, product_amount in reaction.get('products', {}).items():
        if product not in nodes:
            nodes[product] = ChemicalNode(product)
        nodes[product].product_amount = product_amount
        for reactant, details in reaction['reactants'].items():
            nodes[product].reactants[reactant] = details['amount'] / product_amount

# Manually disable sodium and chlorine's association with electrolysis
nodes['Sodium'].reactants = {}
nodes['Chlorine'].reactants = {}

def print_tree(chemical, indent=0):
    if chemical not in nodes or not nodes[chemical].reactants:
        print(" " * indent + f"{chemical} (base ingredient)")
        return

    node = nodes[chemical]
    print(" " * indent + f"{chemical} (produces {node.product_amount})")
    for reactant, amount in node.reactants.items():
        print(" " * (indent + 2) + f"{reactant}: {amount}")
        print_tree(reactant, indent + 4)

def generate_tree_dict(chemical):
    if chemical not in nodes or not nodes[chemical].reactants:
        return {"name": chemical, "type": "base"}

    node = nodes[chemical]
    tree_dict = {"name": chemical, "type": "produced", "amount": node.product_amount, "reactants": []}
    for reactant, amount in node.reactants.items():
        reactant_tree = generate_tree_dict(reactant)
        reactant_tree["amount"] = amount
        tree_dict["reactants"].append(reactant_tree)
    
    return tree_dict


def generate_tree_dict_iterative(chemical, amount=1):
    if chemical not in nodes or not nodes[chemical].reactants:
        print(f"{chemical} has no reactants")
        return {"name": chemical, "type": "base", "amount": amount, "notes": nodes[chemical].notes if chemical in nodes else []}

    tree_dict = {"name": chemical, "type": "produced", "amount": amount, "reactants": [], "notes": nodes[chemical].notes}
    stack = deque([(chemical, amount, tree_dict)])

    while stack:
        current_chemical, current_amount, current_node = stack.pop()
        node = nodes.get(current_chemical)

        # No reactants
        if not node or not node.reactants:
            current_node['type'] = 'base'
            continue

        for reactant, reactant_ratio in node.reactants.items():
            required_amount = round(reactant_ratio * current_amount, 2)  # Scale by the current amount being produced
            reactant_tree = {"name": reactant, "type": "produced", "amount": required_amount, "reactants": [], "notes": nodes[reactant].notes}
            current_node["reactants"].append(reactant_tree)
            stack.append((reactant, required_amount, reactant_tree))

    return tree_dict

# # Example usage
# root_chemical = 'TableSalt'
# tree_dict = generate_tree_dict_iterative(root_chemical)

# now, for every produced item, generate a json tree and toss it in a json array
output = {"chems": []}
for produced in reaction_dict:
    stuff = generate_tree_dict_iterative(produced)
    print(stuff)
    if stuff is not None:
        output['chems'].append(stuff)

with open("file.json", 'w+') as f:
    json.dump(output, f, indent=4)
