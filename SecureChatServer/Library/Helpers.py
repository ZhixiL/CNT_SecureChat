import random
from Library.Consts import *

def keyGeneration():
    return random.randint(0, 2**KEY_LENGTH)

def fakeDES_Encrypt(message, key):
    return message

def fakeDES_Decrypt(message, key):
    return message