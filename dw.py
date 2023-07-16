# Гном состоит из жажды и голода
# Пусть гном будет массивом

class Dwarf:
    def __init__(self):
        self.hunger_level = 100
    
    def feed(self, amount):
        self.hunger_level = min(self.hunger_level + amount, 100)
    
    def starve(self, amount):
        self.hunger_level = max(self.hunger_level - amount, 0)
    
    def get_hunger_level(self):
        return self.hunger_level


