from datetime import time, date, datetime


class Dwarf:
    def __init__(self, name):
        self.name = name
        self.hunger_level = 0

    def feed(self, amount):
        self.hunger_level = min(self.hunger_level + amount, 100)

    def starve(self, amount):
        self.hunger_level = max(self.hunger_level - amount, 0)

    def get_hunger_level(self):
        return self.hunger_level


def level_of_hunger(level):
    if 1 < level <= 10:
        return ("умирает от голода")
    if 10 < level <= 30:
        return ("адски голоден")
    if 30 < level <= 65:
        return ("съел бы целого оленя")
    if 65 < level <= 85:
        return ("умеренно голоден")
    if 85 < level <= 100:
        return ("сыт")
