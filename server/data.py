import os

worldSize = 180
worldFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "world.pkl")
playersDataFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "players.pkl")
imagesFilePath = "serverHTML/static/"
documentName = "documentation.txt"
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
    'forest': [30, 39, 49, 59, 69, 79, 89, 99, 109, 119, 129, 139, 149],
    'desert': [31, 41, 51, 61, 71, 81, 91, 101, 111, 121, 131, 141, 151],
    'tundra': [37, 43, 53, 63, 73, 83, 93, 103, 113, 123, 133, 143, 153],
    'swamp': [33, 45, 55, 65, 75, 85, 95, 105, 115, 125, 135, 145, 155],
    'volcano': [35, 47, 57, 67, 77, 87, 97, 107, 117, 127, 137, 147, 157]
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
    {'type': 'enemy', 'typeId': 4, 'health': 40, 'damage': 0, 'speed': 0.8, 'behavior': 'passive', 'sight': 1, 'walkPause': 0.3, 'attackPause': 0.0, 'allowedBlocks': [0, 1], 'drops': [29]},
    {'type': 'enemy', 'typeId': 5, 'health': 60, 'damage': 20, 'speed': 0.9, 'behavior': 'aggressive', 'sight': 5, 'walkPause': 0.22, 'attackPause': 2.5, 'allowedBlocks': [20, 22], 'drops': [38]},
    {'type': 'enemy', 'typeId': 18, 'health': 80, 'damage': 40, 'speed': 0.9, 'behavior': 'aggressive', 'sight': 7, 'walkPause': 0.22, 'attackPause': 2.5, 'allowedBlocks': [17, 19], 'drops': [34]},
    {'type': 'enemy', 'typeId': 23, 'health': 65, 'damage': 30, 'speed': 0.9, 'behavior': 'aggressive', 'sight': 5, 'walkPause': 0.22, 'attackPause': 2.5, 'allowedBlocks': [6], 'drops': [32]},
    {'type': 'enemy', 'typeId': 24, 'health': 200, 'damage': 50, 'speed': 0.98, 'behavior': 'aggressive', 'sight': 9, 'walkPause': 0.2, 'attackPause': 2.2, 'allowedBlocks': [13, 3], 'drops': [36]},
    {'type': 'player', 'typeId': 27, 'health': 100, 'damage': 15, 'speed': 1.0, 'sight': 5, 'walkPause': 0.2, 'interactPause': 0.5, 'attackPause': 1.5, 'regeneration': 1, 'allowedBlocks': [0, 6, 20, 17, 13, 1, 3, 9, 19, 22], 'swimmingSkill': 0, 'inventory': [], 'equipped': {'head': None, 'back': None, 'hand': None, 'feet': None}, 'chestInventory': [], 'inventorySpace': 10, 'researchProgress': {}, 'skinChangePause': 0.5, 'getDataTimeout': 0.5, 'reach': 1},
    {'type': 'grave', 'typeId': 25, 'inventory': []},
    {'type': 'chest', 'typeId': 28, 'drops': []}
]

# forest: chest drop: Sylvanite(30), enemy drop(4): Anasite(29)
# desert: chest drop: Fulgurite(31), enemy drop(23): Gland(32)
# tundra: chest drop: Borealite(37), enemy drop(5): Peltshard(38)
# swamp: chest drop: Amber(33), enemy drop(18): Bogfang(34)
# volcano: chest drop: Obsidianite(35), enemy drop(24): Pyraplasm(36)

items = [ # 'recipe': {id: amount}
    {'name': 'Anasite', 'recipe': {}, 'typeId': 29, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Sylvanite', 'recipe': {}, 'typeId': 30, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Fulgurite', 'recipe': {}, 'typeId': 31, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Gland', 'recipe': {}, 'typeId': 32, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Amber', 'recipe': {}, 'typeId': 33, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Bogfang', 'recipe': {}, 'typeId': 34, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Obsidianite', 'recipe': {}, 'typeId': 35, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Pyraplasm', 'recipe': {}, 'typeId': 36, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Borealite', 'recipe': {}, 'typeId': 37, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'Peltshard', 'recipe': {}, 'typeId': 38, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'recipe_light_boots_tier_I', 'recipe': {}, 'typeId': 39, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'light_boots_tier_I', 'recipe': {30: 5, 29: 3}, 'typeId': 40, 'boosts': {'speed': 0.1, 'health': 2}, 'bodySlot': ['feet'], 'research': 100.0},
    {'name': 'recipe_light_boots_tier_II', 'recipe': {}, 'typeId': 41, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'light_boots_tier_II', 'recipe': {31: 7, 30: 4, 29: 2}, 'typeId': 42, 'boosts': {'speed': 0.2, 'health': 4}, 'bodySlot': ['feet'], 'research': 130.0},
    {'name': 'recipe_light_boots_tier_III', 'recipe': {}, 'typeId': 43, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'light_boots_tier_III', 'recipe': {37: 9, 31: 5, 30: 3}, 'typeId': 44, 'boosts': {'speed': 0.3, 'health': 8}, 'bodySlot': ['feet'], 'research': 160.0},
    {'name': 'recipe_light_boots_tier_IV', 'recipe': {}, 'typeId': 45, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'light_boots_tier_IV', 'recipe': {33: 12, 37: 6, 32: 4, 29: 2}, 'typeId': 46, 'boosts': {'speed': 0.4, 'health': 16}, 'bodySlot': ['feet'], 'research': 190.0},
    {'name': 'recipe_light_boots_tier_V', 'recipe': {}, 'typeId': 47, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'light_boots_tier_V', 'recipe': {35: 15, 36: 8, 33: 5, 37: 3}, 'typeId': 48, 'boosts': {'speed': 0.5, 'health': 32}, 'bodySlot': ['feet'], 'research': 220.0},
    {'name': 'recipe_heavy_boots_tier_I', 'recipe': {}, 'typeId': 49, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'heavy_boots_tier_I', 'recipe': {29: 7, 30: 3}, 'typeId': 50, 'boosts': {'health': 15, 'speed': -0.1}, 'bodySlot': ['feet'], 'research': 100.0},
    {'name': 'recipe_heavy_boots_tier_II', 'recipe': {}, 'typeId': 51, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'heavy_boots_tier_II', 'recipe': {31: 8, 29: 5, 32: 3}, 'typeId': 52, 'boosts': {'health': 40, 'speed': -0.08}, 'bodySlot': ['feet'], 'research': 130.0},
    {'name': 'recipe_heavy_boots_tier_III', 'recipe': {}, 'typeId': 53, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'heavy_boots_tier_III', 'recipe': {37: 11, 38: 5, 29: 4}, 'typeId': 54, 'boosts': {'health': 65, 'speed': -0.06}, 'bodySlot': ['feet'], 'research': 160.0},
    {'name': 'recipe_heavy_boots_tier_IV', 'recipe': {}, 'typeId': 55, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'heavy_boots_tier_IV', 'recipe': {33: 14, 34: 7, 31: 4, 29: 3}, 'typeId': 56, 'boosts': {'health': 80, 'speed': -0.04}, 'bodySlot': ['feet'], 'research': 190.0},
    {'name': 'recipe_heavy_boots_tier_V', 'recipe': {}, 'typeId': 57, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'heavy_boots_tier_V', 'recipe': {35: 18, 36: 10, 37: 6, 29: 5}, 'typeId': 58, 'boosts': {'health': 110, 'speed': -0.02}, 'bodySlot': ['feet'], 'research': 220.0},
    {'name': 'recipe_backpack_tier_I', 'recipe': {}, 'typeId': 59, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'backpack_tier_I', 'recipe': {30: 8, 29: 4}, 'typeId': 60, 'boosts': {'health': 5, 'inventorySpace': 5, 'speed': -0.07}, 'bodySlot': ['back'], 'research': 100.0},
    {'name': 'recipe_backpack_tier_II', 'recipe': {}, 'typeId': 61, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'backpack_tier_II', 'recipe': {32: 9, 30: 5, 31: 3}, 'typeId': 62, 'boosts': {'health': 12, 'inventorySpace': 10, 'speed': -0.06}, 'bodySlot': ['back'], 'research': 130.0},
    {'name': 'recipe_backpack_tier_III', 'recipe': {}, 'typeId': 63, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'backpack_tier_III', 'recipe': {38: 12, 32: 7, 29: 4}, 'typeId': 64, 'boosts': {'health': 25, 'inventorySpace': 12, 'speed': -0.04}, 'bodySlot': ['back'], 'research': 160.0},
    {'name': 'recipe_backpack_tier_IV', 'recipe': {}, 'typeId': 65, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'backpack_tier_IV', 'recipe': {34: 15, 38: 9, 31: 5}, 'typeId': 66, 'boosts': {'health': 45, 'inventorySpace': 15, 'speed': -0.02}, 'bodySlot': ['back'], 'research': 190.0},
    {'name': 'recipe_backpack_tier_V', 'recipe': {}, 'typeId': 67, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'backpack_tier_V', 'recipe': {36: 20, 34: 11, 37: 7, 30: 5}, 'typeId': 68, 'boosts': {'health': 80, 'inventorySpace': 20}, 'bodySlot': ['back'], 'research': 220.0},
    {'name': 'recipe_helmet_tier_I', 'recipe': {}, 'typeId': 69, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'helmet_tier_I', 'recipe': {29: 7, 30: 4}, 'typeId': 70, 'boosts': {'health': 10}, 'bodySlot': ['head'], 'research': 100.0},
    {'name': 'recipe_helmet_tier_II', 'recipe': {}, 'typeId': 71, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'helmet_tier_II', 'recipe': {31: 9, 32: 5, 29: 3}, 'typeId': 72, 'boosts': {'health': 20}, 'bodySlot': ['head'], 'research': 130.0},
    {'name': 'recipe_helmet_tier_III', 'recipe': {}, 'typeId': 73, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'helmet_tier_III', 'recipe': {37: 12, 38: 7, 31: 4}, 'typeId': 74, 'boosts': {'health': 40}, 'bodySlot': ['head'], 'research': 160.0},
    {'name': 'recipe_helmet_tier_IV', 'recipe': {}, 'typeId': 75, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'helmet_tier_IV', 'recipe': {33: 15, 34: 8, 37: 5, 30: 3}, 'typeId': 76, 'boosts': {'health': 75}, 'bodySlot': ['head'], 'research': 190.0},
    {'name': 'recipe_helmet_tier_V', 'recipe': {}, 'typeId': 77, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'helmet_tier_V', 'recipe': {35: 20, 36: 10, 33: 6, 29: 5}, 'typeId': 78, 'boosts': {'health': 120}, 'bodySlot': ['head'], 'research': 220.0},
    {'name': 'recipe_chestplate_tier_I', 'recipe': {}, 'typeId': 79, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'chestplate_tier_I', 'recipe': {29: 10, 30: 5}, 'typeId': 80, 'boosts': {'health': 20}, 'bodySlot': ['back'], 'research': 100.0},
    {'name': 'recipe_chestplate_tier_II', 'recipe': {}, 'typeId': 81, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'chestplate_tier_II', 'recipe': {31: 12, 29: 7, 32: 4}, 'typeId': 82, 'boosts': {'health': 40}, 'bodySlot': ['back'], 'research': 130.0},
    {'name': 'recipe_chestplate_tier_III', 'recipe': {}, 'typeId': 83, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'chestplate_tier_III', 'recipe': {37: 16, 31: 9, 30: 4}, 'typeId': 84, 'boosts': {'health': 80}, 'bodySlot': ['back'], 'research': 160.0},
    {'name': 'recipe_chestplate_tier_IV', 'recipe': {}, 'typeId': 85, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'chestplate_tier_IV', 'recipe': {33: 20, 37: 11, 32: 5, 29: 4}, 'typeId': 86, 'boosts': {'health': 100}, 'bodySlot': ['back'], 'research': 190.0},
    {'name': 'recipe_chestplate_tier_V', 'recipe': {}, 'typeId': 87, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'chestplate_tier_V', 'recipe': {35: 26, 33: 14, 37: 7, 31: 5}, 'typeId': 88, 'boosts': {'health': 150}, 'bodySlot': ['back'], 'research': 220.0},
    {'name': 'recipe_sword_tier_I', 'recipe': {}, 'typeId': 89, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'sword_tier_I', 'recipe': {29: 7, 30: 5}, 'typeId': 90, 'boosts': {'damage': 10}, 'bodySlot': ['hand'], 'research': 100.0},
    {'name': 'recipe_sword_tier_II', 'recipe': {}, 'typeId': 91, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'sword_tier_II', 'recipe': {31: 10, 32: 4, 29: 3}, 'typeId': 92, 'boosts': {'damage': 15}, 'bodySlot': ['hand'], 'research': 130.0},
    {'name': 'recipe_sword_tier_III', 'recipe': {}, 'typeId': 93, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'sword_tier_III', 'recipe': {37: 13, 38: 6, 31: 4}, 'typeId': 94, 'boosts': {'damage': 20}, 'bodySlot': ['hand'], 'research': 160.0},
    {'name': 'recipe_sword_tier_IV', 'recipe': {}, 'typeId': 95, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'sword_tier_IV', 'recipe': {34: 15, 33: 8, 37: 5, 30: 3}, 'typeId': 96, 'boosts': {'damage': 35}, 'bodySlot': ['hand'], 'research': 190.0},
    {'name': 'recipe_sword_tier_V', 'recipe': {}, 'typeId': 97, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'sword_tier_V', 'recipe': {35: 20, 36: 11, 34: 7, 29: 5}, 'typeId': 98, 'boosts': {'damage': 70}, 'bodySlot': ['hand'], 'research': 220.0},
    {'name': 'recipe_daggers_tier_I', 'recipe': {}, 'typeId': 99, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'daggers_tier_I', 'recipe': {29: 5, 30: 5}, 'typeId': 100, 'boosts': {'damage': 5, 'speed': 0.05, 'attackPause': -0.01}, 'bodySlot': ['hand'], 'research': 100.0},
    {'name': 'recipe_daggers_tier_II', 'recipe': {}, 'typeId': 101, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'daggers_tier_II', 'recipe': {31: 8, 32: 6, 30: 3}, 'typeId': 102, 'boosts': {'damage': 9, 'speed': 0.1, 'attackPause': -0.05}, 'bodySlot': ['hand'], 'research': 130.0},
    {'name': 'recipe_daggers_tier_III', 'recipe': {}, 'typeId': 103, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'daggers_tier_III', 'recipe': {38: 11, 37: 6, 31: 4}, 'typeId': 104, 'boosts': {'damage': 14, 'speed': 0.15, 'attackPause': -0.1}, 'bodySlot': ['hand'], 'research': 160.0},
    {'name': 'recipe_daggers_tier_IV', 'recipe': {}, 'typeId': 105, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'daggers_tier_IV', 'recipe': {34: 14, 33: 8, 38: 5, 29: 3}, 'typeId': 106, 'boosts': {'damage': 25, 'speed': 0.2, 'attackPause': -0.13}, 'bodySlot': ['hand'], 'research': 190.0},
    {'name': 'recipe_daggers_tier_V', 'recipe': {}, 'typeId': 107, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'daggers_tier_V', 'recipe': {36: 18, 35: 10, 34: 6, 32: 4}, 'typeId': 108, 'boosts': {'damage': 48, 'speed': 0.25, 'attackPause': -0.2}, 'bodySlot': ['hand'], 'research': 220.0},
    {'name': 'recipe_healing_amulet_tier_I', 'recipe': {}, 'typeId': 109, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'healing_amulet_tier_I', 'recipe': {30: 7, 29: 3}, 'typeId': 110, 'boosts': {'regeneration': 0.2, 'health': 1}, 'bodySlot': ['hand'], 'research': 100.0},
    {'name': 'recipe_healing_amulet_tier_II', 'recipe': {}, 'typeId': 111, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'healing_amulet_tier_II', 'recipe': {32: 10, 30: 5, 31: 3}, 'typeId': 112, 'boosts': {'regeneration': 0.5, 'health': 3}, 'bodySlot': ['hand'], 'research': 130.0},
    {'name': 'recipe_healing_amulet_tier_III', 'recipe': {}, 'typeId': 113, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'healing_amulet_tier_III', 'recipe': {37: 11, 32: 7, 30: 4}, 'typeId': 114, 'boosts': {'regeneration': 1, 'health': 8}, 'bodySlot': ['hand'], 'research': 160.0},
    {'name': 'recipe_healing_amulet_tier_IV', 'recipe': {}, 'typeId': 115, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'healing_amulet_tier_IV', 'recipe': {33: 14, 37: 8, 32: 4, 29: 3}, 'typeId': 116, 'boosts': {'regeneration': 2, 'health': 15}, 'bodySlot': ['hand'], 'research': 190.0},
    {'name': 'recipe_healing_amulet_tier_V', 'recipe': {}, 'typeId': 117, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'healing_amulet_tier_V', 'recipe': {36: 18, 33: 10, 37: 6, 30: 4}, 'typeId': 118, 'boosts': {'regeneration': 5, 'health': 30}, 'bodySlot': ['hand'], 'research': 220.0},
    {'name': 'recipe_speedy_amulet_tier_I', 'recipe': {}, 'typeId': 119, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'speedy_amulet_tier_I', 'recipe': {29: 4, 30: 7}, 'typeId': 120, 'boosts': {'speed': 0.1, 'attackPause': -0.05}, 'bodySlot': ['hand'], 'research': 100.0},
    {'name': 'recipe_speedy_amulet_tier_II', 'recipe': {}, 'typeId': 121, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'speedy_amulet_tier_II', 'recipe': {31: 9, 30: 5, 29: 3}, 'typeId': 122, 'boosts': {'speed': 0.2, 'attackPause': -0.1}, 'bodySlot': ['hand'], 'research': 130.0},
    {'name': 'recipe_speedy_amulet_tier_III', 'recipe': {}, 'typeId': 123, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'speedy_amulet_tier_III', 'recipe': {37: 12, 31: 6, 30: 4}, 'typeId': 124, 'boosts': {'speed': 0.3, 'attackPause': -0.2}, 'bodySlot': ['hand'], 'research': 160.0},
    {'name': 'recipe_speedy_amulet_tier_IV', 'recipe': {}, 'typeId': 125, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'speedy_amulet_tier_IV', 'recipe': {33: 14, 37: 7, 31: 4}, 'typeId': 126, 'boosts': {'speed': 0.5, 'attackPause': -0.3}, 'bodySlot': ['hand'], 'research': 190.0},
    {'name': 'recipe_speedy_amulet_tier_V', 'recipe': {}, 'typeId': 127, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'speedy_amulet_tier_V', 'recipe': {36: 19, 33: 8, 37: 5, 29: 4}, 'typeId': 128, 'boosts': {'speed': 1.0, 'attackPause': -0.4}, 'bodySlot': ['hand'], 'research': 220.0},
    {'name': 'recipe_heavy_amulet_tier_I', 'recipe': {}, 'typeId': 129, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'heavy_amulet_tier_I', 'recipe': {29: 10, 30: 3}, 'typeId': 130, 'boosts': {'health': 25, 'speed': -0.1}, 'bodySlot': ['hand'], 'research': 100.0},
    {'name': 'recipe_heavy_amulet_tier_II', 'recipe': {}, 'typeId': 131, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'heavy_amulet_tier_II', 'recipe': {31: 11, 29: 7, 32: 3}, 'typeId': 132, 'boosts': {'health': 50, 'speed': -0.12}, 'bodySlot': ['hand'], 'research': 130.0},
    {'name': 'recipe_heavy_amulet_tier_III', 'recipe': {}, 'typeId': 133, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'heavy_amulet_tier_III', 'recipe': {37: 14, 31: 7, 29: 4}, 'typeId': 134, 'boosts': {'health': 80, 'speed': -0.14}, 'bodySlot': ['hand'], 'research': 160.0},
    {'name': 'recipe_heavy_amulet_tier_IV', 'recipe': {}, 'typeId': 135, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'heavy_amulet_tier_IV', 'recipe': {33: 17, 37: 9, 31: 5}, 'typeId': 136, 'boosts': {'health': 100, 'speed': -0.15}, 'bodySlot': ['hand'], 'research': 190.0},
    {'name': 'recipe_heavy_amulet_tier_V', 'recipe': {}, 'typeId': 137, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'heavy_amulet_tier_V', 'recipe': {35: 22, 33: 11, 37: 6, 29: 5}, 'typeId': 138, 'boosts': {'health': 180, 'speed': -0.2}, 'bodySlot': ['hand'], 'research': 220.0},
    {'name': 'recipe_spyglass_tier_I', 'recipe': {}, 'typeId': 139, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'spyglass_tier_I', 'recipe': {30: 6, 29: 3}, 'typeId': 450, 'boosts': {'sight': 1}, 'bodySlot': ['hand'], 'research': 100.0},
    {'name': 'recipe_spyglass_tier_II', 'recipe': {}, 'typeId': 141, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'spyglass_tier_II', 'recipe': {32: 8, 30: 5, 31: 3}, 'typeId': 142, 'boosts': {'sight': 2}, 'bodySlot': ['hand'], 'research': 130.0},
    {'name': 'recipe_spyglass_tier_III', 'recipe': {}, 'typeId': 143, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'spyglass_tier_III', 'recipe': {37: 11, 32: 6, 30: 4}, 'typeId': 144, 'boosts': {'sight': 3}, 'bodySlot': ['hand'], 'research': 160.0},
    {'name': 'recipe_spyglass_tier_IV', 'recipe': {}, 'typeId': 145, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'spyglass_tier_IV', 'recipe': {33: 14, 37: 8, 32: 5, 29: 3}, 'typeId': 146, 'boosts': {'sight': 4}, 'bodySlot': ['hand'], 'research': 190.0},
    {'name': 'recipe_spyglass_tier_V', 'recipe': {}, 'typeId': 147, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'spyglass_tier_V', 'recipe': {36: 18, 35: 10, 33: 6, 31: 4}, 'typeId': 148, 'boosts': {'sight': 6}, 'bodySlot': ['hand'], 'research': 220.0},
    {'name': 'recipe_bow_tier_I', 'recipe': {}, 'typeId': 149, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'bow_tier_I', 'recipe': {29: 6, 30: 4}, 'typeId': 150, 'boosts': {'damage': 4, 'range': 1, 'speed': -0.1}, 'bodySlot': ['hand'], 'research': 100.0},
    {'name': 'recipe_bow_tier_II', 'recipe': {}, 'typeId': 151, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'bow_tier_II', 'recipe': {31: 9, 32: 5, 29: 3}, 'typeId': 152, 'boosts': {'damage': 8, 'range': 1, 'speed': -0.13}, 'bodySlot': ['hand'], 'research': 130.0},
    {'name': 'recipe_bow_tier_III', 'recipe': {}, 'typeId': 153, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'bow_tier_III', 'recipe': {38: 12, 37: 7, 31: 4}, 'typeId': 154, 'boosts': {'damage': 16, 'range': 2, 'speed': -0.12}, 'bodySlot': ['hand'], 'research': 160.0},
    {'name': 'recipe_bow_tier_IV', 'recipe': {}, 'typeId': 155, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'bow_tier_IV', 'recipe': {34: 15, 33: 8, 38: 5, 30: 3}, 'typeId': 156, 'boosts': {'damage': 28, 'range': 3, 'speed': -0.11}, 'bodySlot': ['hand'], 'research': 190.0},
    {'name': 'recipe_bow_tier_V', 'recipe': {}, 'typeId': 157, 'boosts': {}, 'bodySlot': [], 'research': 0.0},
    {'name': 'bow_tier_V', 'recipe': {35: 21, 36: 11, 34: 6, 29: 4}, 'typeId': 158, 'boosts': {'damage': 50, 'range': 5, 'speed': -0.1}, 'bodySlot': ['hand'], 'research': 220.0}
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
