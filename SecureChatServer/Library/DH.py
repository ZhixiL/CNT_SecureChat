# Diffie Hellman implementation
from random import random
from Library.Consts import *

class DH:
    def __init__(self, randomG = 0, randomP = 0):
        self.G = self.genRandomG() if randomG == 0 else randomG
        self.P = self.genRandomP() if randomP == 0 else randomP
        self.pvKey = self.genPrivateKey()
        self.puKey = self.genPublicKey()
        self.symKey = 0
       
    def genRandomG():
        return GH_KEY_LENGTH
    
    def genRandomP():
        return GH_KEY_LENGTH
        
    def genPrivateKey():
        return GH_KEY_LENGTH
    
    def genPublicKey(self):
        return (self.randomG ** self.pvKey) % self.P

    def calcSymKey(self, target_puKey):
        self.symKey = target_puKey ** self.pvKey % self.P
        
    def encrypt(self, pswd):
        return 
    
    def decrypt(self, enc_pswd):
        return