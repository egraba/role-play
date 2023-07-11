import random
import string


def printable_string(length):
    return "".join(random.choice(string.printable) for i in range(length))


def ascii_letters_string(length):
    return "".join(random.choice(string.ascii_letters) for i in range(length))
