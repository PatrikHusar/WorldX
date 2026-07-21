import os

def getObjectInfo(id):
    for object in objects:
        if object['id'] == id:
            return object
    return None

def getObjectList(type):
    objectList = []
    for object in objects:
        if object['type'] == type:
            objectList.append(object)
    return objectList

worldSize = 180
worldFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "world.pkl")
playersFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "players.pkl")
dirs = ['north', 'east', 'south', 'west']
spawnableBlockIds = [0, 17, 20, 6, 13]
spawnPos = (50, 75)
maxEnemiesInZone = {
    'forest': 35,
    'desert': 25,
    'tundra': 20,
    'swamp': 30,
    'volcano': 20
}

# maxChestInZone = {
#     'forest': 30,
#     'desert': 15,
#     'tundra': 15,
#     'swamp': 15,
#     'volcano': 15
# }

# chestsAmount = {
    # 'forest': 0,
    # 'desert': 0,
    # 'tundra': 0,
    # 'swamp': 0,
    # 'volcano': 0
# }


objects = [
    {'type': 'block', 'walkable': True, 'id': 0, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'id': 1, 'swimmable': 1},
    {'type': 'block', 'walkable': False, 'id': 2, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'id': 3, 'swimmable': 2},
    {'type': 'block', 'walkable': True, 'id': 6, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'id': 7, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'id': 8, 'swimmable': False},
    {'type': 'block', 'walkable': True, 'id': 9, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'id': 10, 'swimmable': False, 'interaction': 'openChest'},
    {'type': 'block', 'walkable': False, 'id': 11, 'swimmable': False, 'interaction': 'craft'},
    {'type': 'block', 'walkable': False, 'id': 12, 'swimmable': False, 'interaction': 'research'},
    {'type': 'block', 'walkable': True, 'id': 13, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'id': 14, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'id': 15, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'id': 16, 'swimmable': False},
    {'type': 'block', 'walkable': True, 'id': 17, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'id': 19, 'swimmable': 1.5},
    {'type': 'block', 'walkable': True, 'id': 20, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'id': 21, 'swimmable': False},
    {'type': 'block', 'walkable': True, 'id': 22, 'swimmable': False},
    {'type': 'block', 'walkable': True, 'id': 26, 'swimmable': False},
    {'type': 'enemy', 'id': 4, 'health': 20, 'damage': 0, 'speed': 0.5, 'behavior': 'passive', 'sight': 1, 'pause': 0.25, 'allowedBlocks': [0, 1]},
    {'type': 'enemy', 'id': 5, 'health': 40, 'damage': 25, 'speed': 0.7, 'behavior': 'aggressive', 'sight': 5, 'pause': 0.23, 'allowedBlocks': [20, 22]},
    {'type': 'enemy', 'id': 18, 'health': 80, 'damage': 60, 'speed': 0.8, 'behavior': 'aggressive', 'sight': 7, 'pause': 0.2, 'allowedBlocks': [17, 19]},
    {'type': 'enemy', 'id': 23, 'health': 60, 'damage': 40, 'speed': 0.6, 'behavior': 'aggressive', 'sight': 5, 'pause': 0.23, 'allowedBlocks': [6]},
    {'type': 'enemy', 'id': 24, 'health': 200, 'damage': 100, 'speed': 1, 'behavior': 'aggressive', 'sight': 9, 'pause': 0.18, 'allowedBlocks': [13, 3]},
    {'type': 'grave', 'id': 25, 'health': 1, 'inventory': []},
    {'type': 'player', 'id': 27, 'health': 100, 'damage': 15, 'speed': 1, 'sight': 5, 'pause': 0.18, 'allowedBlocks': [0, 6, 20, 17, 13, 1, 3, 9, 19, 22], 'swimmingSkill': 0, 'inventory': [], 'graves': {}, 'equipped': {'hand': None, 'back': None, 'head': None, 'feet': None}, 'chestInventory': []}
]

zones = [
    {'zone': 'forest', 'block': getObjectInfo(0), 'entities': {}},
    {'zone': 'desert', 'block': getObjectInfo(6), 'entities': {}},
    {'zone': 'tundra', 'block': getObjectInfo(20), 'entities': {}},
    {'zone': 'swamp', 'block': getObjectInfo(17), 'entities': {}},
    {'zone': 'volcano', 'block': getObjectInfo(13), 'entities': {}}
]

# idToName = {
    # 0: 'grass',
    # 1: 'water',
    # 2: 'tree',
    # 3: 'lava',
    # 4: 'duck',
    # 5: 'rat',
    # 6: 'sand',
    # 7: 'sandstone',
    # 8: 'airshipBlock',
    # 9: 'airshipPath',
    # 10: 'chest',
    # 11: 'craftingTable',
    # 12: 'researchStation',
    # 13: 'bassalt',
    # 14: 'volcanicWall',
    # 15: 'deadTree',
    # 16: 'swampTree',
    # 17: 'mud',
    # 18: 'crocodile',
    # 19: 'swampWater',
    # 20: 'snow',
    # 21: 'icespike',
    # 22: 'ice',
    # 23: 'bug',
    # 24: 'golem',
    # 25: 'grave',
    # 26: 'cloud'
# }
