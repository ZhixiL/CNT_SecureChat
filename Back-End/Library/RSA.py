'''
Homework 4, RSA
Name: Zhixi Lin
FSUID: zl19
Due: 03/31/2021, 11:59 PM EDT
The program in this file is the individual work of Zhixi Lin
P.S. My program's efficiency is low, only small number work in a timely manner
'''

import random

class RSA(object):
    #DECORATOR
    def encDecor(self,func):
        def wrapper(number):
            print("The encrypted ", end="")
            func(number)
        return wrapper

    def decDecor(self,func):
        def wrapper(number):
            print("The decrypted ", end="")
            func(number)
        return wrapper


    #Helper Functions
    def LCM(self,e, lambd):#using extended euclidian method here
        oldlambd = lambd  # used to inverse negative result later
        result = 0 # initialize for extended euclidian algorithm
        prevResult = 1
        while lambd != 0:
            q = e // lambd
            e, lambd = lambd, (e % lambd)
            result, prevResult = (prevResult - (q * result)), result
        if prevResult < 0:
            prevResult += oldlambd #reverse result to positive if it's negative
        return prevResult #this is d


    def GCD(self,left, right): #using euclidian method here
        terminate = False
        larger, smaller = int(), int()
        if left>right:
            larger, smaller = left, right
        else:
            larger, smaller = right, left
        gcd = int()
        while(terminate == False):
            temp = larger % smaller
            if(temp == 0):
                terminate = True
            else:
                gcd = temp
                larger, smaller = smaller, gcd
        return gcd


    def totientFunc(self,p,q):
        return (p-1) * (q-1)

    #Main functions
    def __init__(self):
        self.e = 0
        self.d = 0
        self.N = 0 
        self.ls = list()

    def inputFunc(self):
        entries = int(input("Enter the number of messages: "))
        print("Enter the messages:")
        while(entries>0):
            temp = int(input())
            self.ls.append(temp)
            entries-=1

    def printFunc(self, number):
        print("message is " + str(number))
    
    def primeGen(self, minimum):
        curNum = minimum
        primeFound = False
        while primeFound is False: #find prime num by looping over every
            isprime = True          #consequent number after minimum
            for i in range(2, int(curNum/2)):
                if curNum%i == 0:
                    isprime=False
                    break #curNum is found that's not prime, no longer need to further investigate
            if isprime is True:
                primeFound = True
                return curNum
            else:
                curNum+=1


    def keyGen(self):
        minimum = int(input("Enter the minimum value for the prime numbers: "))
        p = self.primeGen(minimum)
        q = self.primeGen(random.randrange(p+1,p+100)) #ensure p and q are not the same
        self.N = p*q

        #generate e
        lambd = self.totientFunc(p,q)
        self.e=random.randrange(100,1000)#ensure e is fairly large
        while(self.GCD(self.e,lambd) >1):
            self.e=random.randrange(100,1000)
        self.d = self.LCM(self.e,lambd)

        print("N is",self.N)
        print("e is",self.e)

    def encrypt(self, plain):
        return (plain**self.e) % self.N

    def decrypt(self, cipher):
        return (cipher**self.d) % self.N

    def messages(self):
        self.inputFunc()
        self.keyGen()
        encryptedLs = list()
        decryptedLs = list()
        for num in self.ls:
            enc = self.encrypt(num)
            encryptedLs.append(enc)
        for enc in encryptedLs:
            encMsgPrint = self.encDecor(self.printFunc)
            encMsgPrint(number=enc)
    
        for num in encryptedLs:
            dec = self.decrypt(num)
            decryptedLs.append(dec)
        for dec in decryptedLs:
            decMsgPrint = self.decDecor(self.printFunc)
            decMsgPrint(number=dec)


if __name__ == "__main__":
    rsa = RSA()
    rsa.messages()