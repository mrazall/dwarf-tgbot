

class Pickaxe:
    def __init__(self, level, durability):
        self.level = level
        self.durability = durability
        self.gold_per_strike = level

    def mine_gold(self):
        if self.durability > 0:
            gold_obtained = self.gold_per_strike * self.level
            self.durability -= 3
            return gold_obtained
        else:
            return 0

    def upgrade(self):
        if self.level < 10:
            self.level += 1
            self.gold_per_strike += 1
            self.durability = 100

    def set_level(self, new_level):
        if 1 <= new_level <= 10:
            self.level = new_level

    def is_broken(self):
        return self.durability <= 0


