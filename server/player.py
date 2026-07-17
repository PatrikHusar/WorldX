import data

class Player:
    def __init__(self, pos):
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.health = 100
        self.dir = 'north'
        self.isMoving = False
        
        self.entity = {
            'id': 99,
            'type': 'player',
            'zone': 'forest',
            'properties': {
                'health': self.health,
                'inventory': ['iron_sword', 'apple', 'health_potion']
            }
        }
        self.chestInventory = []
        self.inventory = self.entity['properties']['inventory']
        self.graves = []

    def restorePlayer(self, chestInventory, inventory, graves):
        self.chestInventory = chestInventory
        self.inventory = inventory
        self.entity['properties']['inventory'] = inventory
        self.graves = graves