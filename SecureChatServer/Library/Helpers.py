import random
from Library.Consts import *

def keyGeneration():
    return str(random.randint(0, 2**KEY_LENGTH))

def getIntKey(input):
    return int(input)