import random
import string


def generate_random_string(length):
    return "".join(random.choice(string.printable) for i in range(length))


def generate_random_name(length):
    return "".join(random.choice(string.ascii_letters) for i in range(length))
