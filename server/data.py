import copy
import os

def getObjectInfo(id):
    for object in objects:
        if object['typeId'] == id:
            return copy.deepcopy(object)
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
maxChestInZone = {
    'forest': 40,
    'desert': 20,
    'tundra': 35,
    'swamp': 35,
    'volcano': 20
}

chestDrops = {
    'forest': [29],
    'desert': [31],
    'tundra': [37],
    'swamp': [33],
    'volcano': [35]
}

objects = [
    {'type': 'block', 'walkable': True, 'typeId': 0, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'typeId': 1, 'swimmable': 1},
    {'type': 'block', 'walkable': False, 'typeId': 2, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'typeId': 3, 'swimmable': 2},
    {'type': 'block', 'walkable': True, 'typeId': 6, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'typeId': 7, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'typeId': 8, 'swimmable': False},
    {'type': 'block', 'walkable': True, 'typeId': 9, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'typeId': 10, 'swimmable': False, 'interaction': 'openChest'},
    {'type': 'block', 'walkable': False, 'typeId': 11, 'swimmable': False, 'interaction': 'craft'},
    {'type': 'block', 'walkable': False, 'typeId': 12, 'swimmable': False, 'interaction': 'research'},
    {'type': 'block', 'walkable': True, 'typeId': 13, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'typeId': 14, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'typeId': 15, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'typeId': 16, 'swimmable': False},
    {'type': 'block', 'walkable': True, 'typeId': 17, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'typeId': 19, 'swimmable': 1.5},
    {'type': 'block', 'walkable': True, 'typeId': 20, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'typeId': 21, 'swimmable': False},
    {'type': 'block', 'walkable': True, 'typeId': 22, 'swimmable': False},
    {'type': 'block', 'walkable': True, 'typeId': 26, 'swimmable': False},
    {'type': 'enemy', 'typeId': 4, 'health': 20, 'damage': 0, 'speed': 0.5, 'behavior': 'passive', 'sight': 1, 'pause': 0.25, 'allowedBlocks': [0, 1], 'drops': [28]},
    {'type': 'enemy', 'typeId': 5, 'health': 40, 'damage': 25, 'speed': 0.7, 'behavior': 'aggressive', 'sight': 5, 'pause': 0.23, 'allowedBlocks': [20, 22], 'drops': [38]},
    {'type': 'enemy', 'typeId': 18, 'health': 80, 'damage': 50, 'speed': 0.8, 'behavior': 'aggressive', 'sight': 7, 'pause': 0.2, 'allowedBlocks': [17, 19], 'drops': [34]},
    {'type': 'enemy', 'typeId': 23, 'health': 60, 'damage': 40, 'speed': 0.6, 'behavior': 'aggressive', 'sight': 5, 'pause': 0.23, 'allowedBlocks': [6], 'drops': [32]},
    {'type': 'enemy', 'typeId': 24, 'health': 200, 'damage': 70, 'speed': 1, 'behavior': 'aggressive', 'sight': 9, 'pause': 0.18, 'allowedBlocks': [13, 3], 'drops': [36]},
    {'type': 'grave', 'typeId': 25, 'drops': []},
    {'type': 'player', 'typeId': 27, 'health': 100, 'damage': 15, 'speed': 1, 'sight': 5, 'pause': 0.18, 'regeneration': 2, 'allowedBlocks': [0, 6, 20, 17, 13, 1, 3, 9, 19, 22], 'swimmingSkill': 0, 'inventory': [], 'graves': {}, 'equipped': {'head': None, 'back': None, 'hand': None, 'feet': None}, 'chestInventory': [], 'inventorySpace': 10},
    {'type': 'chest', 'typeId': 30, 'drops': []}
]

items = [
    {'name': 'Anasite', 'recipe': None, 'typeId': 28, 'boosts': {}, 'bodySlot': None, 'research': 0.0},
    {'name': 'Sylvanite', 'recipe': None, 'typeId': 29, 'boosts': {}, 'bodySlot': None, 'research': 0.0},
    {'name': 'Fulgurite', 'recipe': None, 'typeId': 31, 'boosts': {}, 'bodySlot': None, 'research': 0.0},
    {'name': 'Gland', 'recipe': None, 'typeId': 32, 'boosts': {}, 'bodySlot': None, 'research': 0.0},
    {'name': 'Amber', 'recipe': None, 'typeId': 33, 'boosts': {}, 'bodySlot': None, 'research': 0.0},
    {'name': 'Bogfang', 'recipe': None, 'typeId': 34, 'boosts': {}, 'bodySlot': None, 'research': 0.0},
    {'name': 'Obsidianite', 'recipe': None, 'typeId': 35, 'boosts': {}, 'bodySlot': None, 'research': 0.0},
    {'name': 'Pyraplasm', 'recipe': None, 'typeId': 36, 'boosts': {}, 'bodySlot': None, 'research': 0.0},
    {'name': 'Borealite', 'recipe': None, 'typeId': 37, 'boosts': {}, 'bodySlot': None, 'research': 0.0},
    {'name': 'Peltshard', 'recipe': None, 'typeId': 38, 'boosts': {}, 'bodySlot': None, 'research': 0.0}
]

entitySpawn = {
    'forest': getObjectInfo(4),
    'tundra': getObjectInfo(5),
    'swamp': getObjectInfo(18),
    'desert': getObjectInfo(23),
    'volcano': getObjectInfo(24)
}

zones = [
    {'zone': 'forest', 'block': getObjectInfo(0), 'entities': {}},
    {'zone': 'desert', 'block': getObjectInfo(6), 'entities': {}},
    {'zone': 'tundra', 'block': getObjectInfo(20), 'entities': {}},
    {'zone': 'swamp', 'block': getObjectInfo(17), 'entities': {}},
    {'zone': 'volcano', 'block': getObjectInfo(13), 'entities': {}}
]

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
# 30: 'treasureChest'
