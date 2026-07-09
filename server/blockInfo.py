info = [
    {'name': 'grass', 'type': 'block', 'canWalkOn': True, 'id': 0, 'properties': {}},
    {'name': 'water', 'type': 'liquid', 'canWalkOn': False, 'id': 1, 'properties': {}},
    {'name': 'tree', 'type': 'block', 'canWalkOn': False, 'id': 2, 'properties': {}},
    {'name': 'stone', 'type': 'block', 'canWalkOn': False, 'id': 3, 'properties': {}}
]

def getBlockInfo(block_id):
    for block in info:
        if block['id'] == block_id:
            return block
    return None
def getBlockList():
    return info