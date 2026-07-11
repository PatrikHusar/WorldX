
zones = ['forest', 'desert', 'tundra', 'swamp', 'volcano', 'airship']
dirs = ['north', 'east', 'south', 'west']


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
    {'zone': 'forest', 'type': 'block', 'walkable': True, 'id': 0, 'properties': {}},
    {'zone': 'forest', 'type': 'block', 'walkable': False, 'id': 1, 'properties': {'swimmable': 1}},
    {'zone': 'forest', 'type': 'block', 'walkable': False, 'id': 2, 'properties': {}},
    {'zone': 'volcano', 'type': 'block', 'walkable': False, 'id': 3, 'properties': {'swimmable': 2}},
    {'zone': 'forest', 'type': 'enemy', 'id': 4, 'properties': {'health': 3, 'damage': 0, 'speed': 0.5, 'behavior': 'passive', 'sight': 5, 'pause': 0.25}},
    # {'zone': 'tundra', 'type': 'enemy','id': 5, 'properties': {'health': 10, 'damage': 1, 'speed': 1.5, 'behavior': 'neutral', 'deagroTime': 30}}
    {'zone': 'desert', 'type': 'block', 'walkable': True, 'id': 6, 'properties': {}},
    {'zone': 'desert', 'type': 'block', 'walkable': False, 'id': 7, 'properties': {}},
    {'zone': 'airship', 'type': 'block', 'walkable': False, 'id': 8, 'properties': {}},
    {'zone': 'airship', 'type': 'block', 'walkable': True, 'id': 9, 'properties': {}},
    {'zone': 'airship', 'type': 'block', 'walkable': False, 'id': 10, 'properties': {'interaction': 'openChest'}},
    {'zone': 'airship', 'type': 'block', 'walkable': False, 'id': 11, 'properties': {'interaction': 'craft'}},
    {'zone': 'airship', 'type': 'block', 'walkable': False, 'id': 12, 'properties': {'interaction': 'research'}},
    {'zone': 'volcano', 'type': 'block', 'walkable': True, 'id': 13, 'properties': {}},
    {'zone': 'volcano', 'type': 'block', 'walkable': False, 'id': 14, 'properties': {}},
    {'zone': 'volcano', 'type': 'block', 'walkable': False, 'id': 15, 'properties': {}},
    {'zone': 'swamp', 'type': 'block', 'walkable': False, 'id': 16, 'properties': {}},
    {'zone': 'swamp', 'type': 'block', 'walkable': True, 'id': 17, 'properties': {}},
    {'zone': 'swamp', 'type': 'enemy', 'id': 18, 'properties': {'health': 10, 'damage': 3, 'speed': 0.8, 'behavior': 'aggresive', 'sight': 7, 'pause': 0.2}},
    {'zone': 'swamp', 'type': 'block', 'walkable': False, 'id': 19, 'properties': {'swimmable': 1}}
]

idToName = {
    0: 'grass',
    1: 'water',
    2: 'tree',
    3: 'lava',
    4: 'duck',
    # 5: 'hog',
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
    19: 'swampWater'
}


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
