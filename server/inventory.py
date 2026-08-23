def addItemToInventory(player, item, ignoreSpace=False):
    if player.eDetails['inventorySpace'] > 0 or ignoreSpace:
        player.eDetails['inventory'].append(item)
        player.eDetails['inventorySpace'] -= 1
def delItemFromInventory(player, item):
    try:
        player.eDetails['inventory'].remove(item)
        player.eDetails['inventorySpace'] += 1
    except:
        pass
def equipItemToSlot(player, item, slot):
    player.eDetails['equipped'][slot] = item
    delItemFromInventory(player, item)
def unequipItemFromSlot(player, slot):
    item = player.eDetails['equipped'][slot]
    player.eDetails['equipped'][slot] = None
    addItemToInventory(player, item, ignoreSpace=True)
    return item
def storeItemToChest(player, item):
    delItemFromInventory(player, item)
    player.eDetails['chestInventory'].append(item)
def takeItemFromChest(player, item):
    addItemToInventory(player, item, ignoreSpace=True)
    player.eDetails['chestInventory'].remove(item)
def restorePlayerData(player, restore):
    setChestInventory(player, restore['chestInventory'])
    setInventory(player, restore['inventory'])
    setResearchProgress(player, restore['researchProgress'])
    player.name = restore['name']
def savePlayerData(player):
    saveData = {}
    saveData['chestInventory'] = getChestInventory(player)
    inv = getInventory(player).copy()
    for slot in getEquipped(player):
        if getEquipped(player, slot):
            inv.append(getEquipped(player, slot))
    saveData['inventory'] = inv
    saveData['name'] = player.name
    saveData['researchProgress'] = getResearchProgress(player)
    return saveData

def setHealth(ent, hp):
    ent.eDetails['health'] = hp
def setChestInventory(player, inv):
    player.eDetails['chestInventory'] = inv
def setInventory(player, inv):
    for item in inv:
        addItemToInventory(player, item, ignoreSpace=True)
def setResearchProgress(player, res):
    player.eDetails['researchProgress'] = res


def getInventory(ent):
    return ent.eDetails.get('inventory', [])
def getEquipped(player, slot=None):
    if slot:
        return player.eDetails.get('equipped')[slot]
    else:
        return player.eDetails.get('equipped', {})
def getHealth(ent):
    return ent.eDetails.get('health')
def getTypeId(ent):
    return ent.eDetails.get('typeId', 0)
def getDamage(ent):
    return ent.eDetails.get('damage')
def getAttackPause(ent):
    return ent.eDetails.get('attackPause')
def getBlockTypeId(block):
    return block.get('typeId')
def getChestInventory(player):
    return player.eDetails.get('chestInventory')
def getResearchProgress(player):
    return player.eDetails.get('researchProgress')
def getAllowedBlocks(player):
    return player.eDetails.get('allowedBlocks')
def getBlockSwimmable(block):
    return block['swimmable']
def getSwimmingSkill(player):
    return player.eDetails.get('swimmingSkill', 0)
def getSpeed(ent):
    return ent.eDetails.get('speed', 0)
def getWalkPause(ent):
    return ent.eDetails.get('walkPause', 1)
def getSight(ent):
    return ent.eDetails.get('sight', 0)
def getDir(ent):
    return getattr(ent, 'dir', 'north')
def getMyId(ent):
    return getattr(ent, 'myId', -1)
def getName(ent):
    return getattr(ent, 'name', None)
def getDrops(ent):
    return ent.eDetails.get('drops', None)
def getSkinUpdatePause(ent):
    return ent.eDetails.get('skinChangePause', 1)
def getGetTimeout(player):
    return player.eDetails.get('getTimeout', 1)