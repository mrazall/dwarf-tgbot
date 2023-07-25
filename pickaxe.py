class Pickaxe:
    def __init__(self, level=1, durability=100, gold_per_strike=1):
        self.level = level
        self.durability = durability
        self.gold_per_strike = gold_per_strike

    def mine_gold(self):
        if self.durability > 0:
            gold_obtained = self.gold_per_strike * self.level
            self.durability -= 10  # Предполагаем, что за один удар теряется 10 единиц прочности
            return gold_obtained
        else:
            return 0

    def upgrade(self):
        if self.level < 10:
            self.level += 1
            self.gold_per_strike += 1
            self.durability = 100

    def is_broken(self):
        return self.durability <= 0
