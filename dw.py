

class Dwarf:
    def __init__(self, name):
        self.name = name
        self.hunger_level = 0
        self.thirst_level = 0

    def feed(self, amount):
        self.hunger_level = min(self.hunger_level + amount, 100)

    def starve(self, amount):
        self.hunger_level = max(self.hunger_level - amount, 0)

    def get_hunger_level(self):
        return self.hunger_level

    def drink(self, amount):
        self.thirst_level = min(self.thirst_level + amount, 100)

    def crave(self, amount):
        self.thirst_level = max(self.thirst_level - amount, 0)

    def get_thirst_level(self):
        return self.thirst_level



def level_of_hunger(level):
    if 1 < level <= 10:
        return 1
    if 10 < level <= 30:
        return 2
    if 30 < level <= 65:
        return 3
    if 65 < level <= 85:
        return 4
    if 85 < level <= 100:
        return 5


def level_of_thirst(level):
    if 0 <= level <= 30:
        return 1
    if 30 < level <= 65:
        return 2
    if 65 < level <= 100:
        return 3





