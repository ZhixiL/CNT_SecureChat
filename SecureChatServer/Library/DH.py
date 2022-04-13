# Diffie Hellman implementation
from ast import Num
from random import random
from Library.Consts import *

class DH:
    def __init__(self, inputG = 0, inputP = 0):
        # make sure that G is less than p.
        self.G = self.genPrime(DH_KEY_LENGTH) if inputG == 0 else inputG
        self.P = self.genPrime(DH_KEY_LENGTH+1) if inputP == 0 else inputP
        self.pvKey = self.genPrivateKey(DH_KEY_LENGTH)
        self.puKey = self.genPublicKey()
        self.symKey = 0
        
    def genPrivateKey(length):
        return (random.randrange(2**(length-1)+1, 2**length-1))
    
    def genPublicKey(self):
        return (self.randomG ** self.pvKey) % self.P

    def calcSymKey(self, target_puKey):
        self.symKey = target_puKey ** self.pvKey % self.P
        
    def encrypt(self, pswd):
        return 
    
    def decrypt(self, enc_pswd):
        return