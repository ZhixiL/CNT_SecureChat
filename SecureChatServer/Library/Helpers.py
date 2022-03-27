import random
from Library.Consts import *

def keyGeneration():
    return random.randint(0, 10**KEY_LENGTH)