blocks = [
    {'name': 'grass', 'type': 'block', 'canWalkOn': True, 'id': 0, 'properties': {}},
    {'name': 'water', 'type': 'liquid', 'canWalkOn': False, 'id': 1, 'properties': {}},
    {'name': 'tree', 'type': 'block', 'canWalkOn': False, 'id': 2, 'properties': {}},
    {'name': 'stone', 'type': 'block', 'canWalkOn': False, 'id': 3, 'properties': {}},
]
enemies = [
    {'name': 'duck', 'type': 'enemy', 'canWalkOn': True, 'id': 4, 'properties': {'health': 3, 'damage': 0, 'speed': 1, 'behavior': 'passive'}},
    {'name': 'hog', 'type': 'enemy', 'canWalkOn': True, 'id': 5, 'properties': {'health': 10, 'damage': 1, 'speed': 1.5, 'behavior': 'neutral'}}
]

def getBlockInfo(blockId):
    for block in blocks:
        if block['id'] == blockId:
            return block
    return None
def getBlockList():
    return blocks
def getEnemyList():
    return enemies
def getEnemyInfo(enemyId):
    for e in enemies:
        if e['id'] == enemyId:
            return e
    return None