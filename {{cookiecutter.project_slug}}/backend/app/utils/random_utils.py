import random

class RandomDigits():

    def four_digits():
        data = random.randint(1000, 9999)
        return str(data)

    def six_digits():
        data = random.randint(100000, 999999)
        return str(data)