import random

def getObjectInfo(id):
    for object in objects:
        if object['id'] == id:
            return object
    return None

def getObjectList(type):
    eList = []
    for object in objects:
        if object['type'] == type:
            eList.append(object)
    return eList

def transferIdMap(map):
    newMap = []
    for r in map:
        row = []
        for c in r:
            row.append(getObjectInfo(c))
        newMap.append(row)
    return newMap



zones = ['forest', 'desert', 'tundra', 'swamp', 'volcano', 'airship']
dirs = ['north', 'east', 'south', 'west']
spawnableBlocks = [0, 17, 20, 6, 13]

maxEnemiesInZone = {
    'forest': 30,
    'desert': 15,
    'tundra': 15,
    'swamp': 15,
    'volcano': 15
}

maxChestInZone = {
    'forest': 30,
    'desert': 15,
    'tundra': 15,
    'swamp': 15,
    'volcano': 15
}

chestsAmount = {
    'forest': 0,
    'desert': 0,
    'tundra': 0,
    'swamp': 0,
    'volcano': 0
}

objects = [
    {'zone': 'forest', 'type': 'block', 'walkable': True, 'id': 0, 'properties': {'swimmable': False}},
    {'zone': 'forest', 'type': 'block', 'walkable': False, 'id': 1, 'properties': {'swimmable': 1}},
    {'zone': 'forest', 'type': 'block', 'walkable': False, 'id': 2, 'properties': {'swimmable': False}},
    {'zone': 'volcano', 'type': 'block', 'walkable': False, 'id': 3, 'properties': {'swimmable': 2}},
    {'zone': 'forest', 'type': 'enemy', 'id': 4, 'properties': {'health': 20, 'damage': 0, 'speed': 0.5, 'behavior': 'passive', 'sight': 1, 'pause': 0.25, 'swimmingSkill': 1}},
    {'zone': 'tundra', 'type': 'enemy', 'id': 5, 'properties': {'health': 40, 'damage': 25, 'speed': 0.7, 'behavior': 'aggressive', 'sight': 5, 'pause': 0.23, 'swimmingSkill': 0}},
    {'zone': 'desert', 'type': 'block', 'walkable': True, 'id': 6, 'properties': {'swimmable': False}},
    {'zone': 'desert', 'type': 'block', 'walkable': False, 'id': 7, 'properties': {'swimmable': False}},
    {'zone': 'airship', 'type': 'block', 'walkable': False, 'id': 8, 'properties': {'swimmable': False}},
    {'zone': 'airship', 'type': 'block', 'walkable': True, 'id': 9, 'properties': {'swimmable': False}},
    {'zone': 'airship', 'type': 'block', 'walkable': False, 'id': 10, 'properties': {'interaction': 'openChest', 'swimmable': False}},
    {'zone': 'airship', 'type': 'block', 'walkable': False, 'id': 11, 'properties': {'interaction': 'craft', 'swimmable': False}},
    {'zone': 'airship', 'type': 'block', 'walkable': False, 'id': 12, 'properties': {'interaction': 'research', 'swimmable': False}},
    {'zone': 'volcano', 'type': 'block', 'walkable': True, 'id': 13, 'properties': {'swimmable': False}},
    {'zone': 'volcano', 'type': 'block', 'walkable': False, 'id': 14, 'properties': {'swimmable': False}},
    {'zone': 'volcano', 'type': 'block', 'walkable': False, 'id': 15, 'properties': {'swimmable': False}},
    {'zone': 'swamp', 'type': 'block', 'walkable': False, 'id': 16, 'properties': {'swimmable': False}},
    {'zone': 'swamp', 'type': 'block', 'walkable': True, 'id': 17, 'properties': {'swimmable': False}},
    {'zone': 'swamp', 'type': 'enemy', 'id': 18, 'properties': {'health': 80, 'damage': 60, 'speed': 0.8, 'behavior': 'aggressive', 'sight': 7, 'pause': 0.2, 'swimmingSkill': 1.5}},
    {'zone': 'swamp', 'type': 'block', 'walkable': False, 'id': 19, 'properties': {'swimmable': 1.5}},
    {'zone': 'tundra', 'type': 'block', 'walkable': True, 'id': 20, 'properties': {'swimmable': False}},
    {'zone': 'tundra', 'type': 'block', 'walkable': False, 'id': 21, 'properties': {'swimmable': False}},
    {'zone': 'tundra', 'type': 'block', 'walkable': True, 'id': 22, 'properties': {'swimmable': False}},
    {'zone': 'desert', 'type': 'enemy', 'id': 23, 'properties': {'health': 60, 'damage': 40, 'speed': 0.6, 'behavior': 'aggressive', 'sight': 5, 'pause': 0.23, 'swimmingSkill': 0}},
    {'zone': 'volcano', 'type': 'enemy', 'id': 24, 'properties': {'health': 200, 'damage': 100, 'speed': 1, 'behavior': 'aggressive', 'sight': 9, 'pause': 0.18, 'swimmingSkill': 2}},
    {'zone': 'grave', 'type': 'enemy', 'id': 25, 'properties': {'health': 1, 'damage': 0, 'speed': 0.0, 'behavior': 'passive', 'sight': 0, 'pause': 0.0, 'swimmingSkill': 0}},
    {'zone': 'cloud', 'type': 'enemy', 'id': 26, 'properties': {'health': 1, 'damage': 0, 'speed': 0.0, 'behavior': 'passive', 'sight': 0, 'pause': 0.0, 'swimmingSkill': 0}}
]

idToName = {
    0: 'grass',
    1: 'water',
    2: 'tree',
    3: 'lava',
    4: 'duck',
    5: 'rat',
    6: 'sand',
    7: 'sandstone',
    8: 'airshipBlock',
    9: 'airshipPath',
    10: 'chest',
    11: 'craftingTable',
    12: 'researchStation',
    13: 'bassalt',
    14: 'volcanicWall',
    15: 'deadTree',
    16: 'swampTree',
    17: 'mud',
    18: 'crocodile',
    19: 'swampWater',
    20: 'snow',
    21: 'icespike',
    22: 'ice',
    23: 'bug',
    24: 'golem',
    25: 'grave',
    26: 'cloud'
}

