import os

worldSize = 180
worldFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "world.pkl")
playersFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "players.pkl")
dirs = ['north', 'east', 'south', 'west']
spawnableBlockIds = [0, 17, 20, 6, 13]
noPVPzones = ['forest']
spawnPos = (50, 75)
researchValue = 10
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
    'forest': [29, 39],
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
    {'type': 'block', 'walkable': False, 'typeId': 10, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'typeId': 11, 'swimmable': False},
    {'type': 'block', 'walkable': False, 'typeId': 12, 'swimmable': False},
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
    {'type': 'enemy', 'typeId': 4, 'health': 40, 'damage': 0, 'speed': 0.8, 'behavior': 'passive', 'sight': 1, 'walkPause': 0.3, 'attackPause': 0.0, 'allowedBlocks': [0, 1], 'drops': [28]},
    {'type': 'enemy', 'typeId': 5, 'health': 60, 'damage': 20, 'speed': 0.9, 'behavior': 'aggressive', 'sight': 5, 'walkPause': 0.22, 'attackPause': 2.5, 'allowedBlocks': [20, 22], 'drops': [38]},
    {'type': 'enemy', 'typeId': 18, 'health': 80, 'damage': 40, 'speed': 0.9, 'behavior': 'aggressive', 'sight': 7, 'walkPause': 0.22, 'attackPause': 2.5, 'allowedBlocks': [17, 19], 'drops': [34]},
    {'type': 'enemy', 'typeId': 23, 'health': 65, 'damage': 30, 'speed': 0.9, 'behavior': 'aggressive', 'sight': 5, 'walkPause': 0.22, 'attackPause': 2.5, 'allowedBlocks': [6], 'drops': [32]},
    {'type': 'enemy', 'typeId': 24, 'health': 200, 'damage': 50, 'speed': 0.95, 'behavior': 'aggressive', 'sight': 9, 'walkPause': 0.2, 'attackPause': 2.2, 'allowedBlocks': [13, 3], 'drops': [36]},
    {'type': 'player', 'typeId': 27, 'health': 100, 'damage': 15, 'speed': 0.95, 'sight': 5, 'walkPause': 0.2, 'attackPause': 1.5, 'regeneration': 1, 'allowedBlocks': [0, 6, 20, 17, 13, 1, 3, 9, 19, 22], 'swimmingSkill': 0, 'inventory': [], 'equipped': {'head': None, 'back': None, 'hand': None, 'feet': None}, 'chestInventory': [], 'inventorySpace': 10, 'researchProgress': {}},
    {'type': 'grave', 'typeId': 25, 'inventory': []},
    {'type': 'chest', 'typeId': 30, 'drops': []}
]

items = [ # 'recipe': {id: amount}
    {'name': 'Anasite', 'recipe': {}, 'typeId': 28, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Sylvanite', 'recipe': {}, 'typeId': 29, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Fulgurite', 'recipe': {}, 'typeId': 31, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Gland', 'recipe': {}, 'typeId': 32, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Amber', 'recipe': {}, 'typeId': 33, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Bogfang', 'recipe': {}, 'typeId': 34, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Obsidianite', 'recipe': {}, 'typeId': 35, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Pyraplasm', 'recipe': {}, 'typeId': 36, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Borealite', 'recipe': {}, 'typeId': 37, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Peltshard', 'recipe': {}, 'typeId': 38, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'recipe_light_boots_tier_1', 'recipe': {}, 'typeId': 39, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'light_boots_tier_1', 'recipe': {29: 2}, 'typeId': 40, 'boosts': {'speed': 0.1}, 'bodySlot': ['feet'], 'research': 10.0}
]

entitySpawn = {
    'forest': 4,
    'tundra': 5,
    'swamp': 18,
    'desert': 23,
    'volcano': 24
}

zones = [
    {'zone': 'forest', 'block': 0, 'entities': {}},
    {'zone': 'desert', 'block': 6, 'entities': {}},
    {'zone': 'tundra', 'block': 20, 'entities': {}},
    {'zone': 'swamp', 'block': 17, 'entities': {}},
    {'zone': 'volcano', 'block': 13, 'entities': {}}
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

PREFIXES = [
    "Shadow", "Iron", "Storm", "Frost", "Fire", "Swift", 
    "Dark", "Silver", "Gold", "Wild", "Brave", "Silent",
    "Thunder", "Mystic", "Cosmic", "Lunar", "Solar", "Night"
]

SUFFIXES = [
    "Wolf", "Hawk", "Blade", "Stone", "Fox", "Bear", 
    "River", "Star", "Moon", "Sun", "Fang", "Claw",
    "Hunter", "Walker", "Stalker", "Rider", "Ghost", "Shield"
]
