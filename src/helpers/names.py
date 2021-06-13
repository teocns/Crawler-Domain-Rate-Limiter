import names
import random


def get_nickname():
    name = names.get_last_name()
    num = random.randint(1, 999999)
    return "#" + name + str(num)
