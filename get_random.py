import random



def random_output():
    a = random.randint(1, 100)
    if 1 <= a <= 20:
        return 0
    if 20 < a <= 30:
        return random.randint(1, 3)
    if 30 < a <= 70:
        return random.randint(3, 5)
    if 70 < a <= 95:
        return random.randint(5, 7)
    if 95 < a <= 100:
        return random.randint(7, 10)
    

def random_pickaxe():
    a = random.randint(1000, 10300)
    return (a//1000)

