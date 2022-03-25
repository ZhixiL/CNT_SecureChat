import sys, random
from datetime import datetime

#initial permutation for 64 bits
IP = [58,50,42,34,26,18,10,2,60,52,44,
    36,28,20,12,4,62,54,46,38,30,22,14,6,64,
    56,48,40,32,24,16,8,57,49,41,33,25,17,9,
    1,59,51,43,35,27,19,11,3,61,53,45,37,29,
    21,13,5,63,55,47,39,31,23,15,7]

#inverting the initial permutation
IP_INVERT = [40,8,48,16,56,24,64,32,39,7,47,
    15,55,23,63,31,38,6,46,14,54,22,62,30,37,
    5,45,13,53,21,61,29,36,4,44,12,52,20,60,28,
    35,3,43,11,51,19,59,27,34,2,42,10,50,18,58,
    26,33,1,41,9,49,17,57,25]

#permutate 56bits to 48 bits    
PC2 = [14,17,11,24,1,5,3,28,15,
    6,21,10,23,19,12,4,26,8,16,7,27,
    20,13,2,41,52,31,37,47,55,30,40,
    51,45,33,48,44,49,39,56,34,53,46,
    42,50,36,29,32]

#intermediary permutation, 32 bits
P_INT = [16,7,20,21,29,12,28,17,1,15,
    23,26,5,18,31,10,2,8,24,14,32,27,
    3,9,19,13,30,6,22,11,4,25]

#sBox
SBOX = [14,4,13,1,2,15,11,8,3,10,6,12,
    5,9,0,7,0,15,7,4,14,2,13,1,10,6,12,
    11,9,5,3,8,4,1,14,8,13,6,2,11,15,12,
    9,7,3,10,5,0,15,12,8,2,4,9,1,7,5,11,
    3,14,10,0,6,13]

#expand the 32 bits to 48 bits
EXPAND = [32,1,2,3,4,5,4,5,6,7,8,9,8,9
    ,10,11,12,13,12,13,14,15,16,17,16,
    17,18,19,20,21,20,21,22,23,24,25,24,
    25,26,27,28,29,28,29,30,31,32,1]

def permutate(inp, schedule, length):
    finval = 0 #length denotes the input bit size
    for location in schedule:
        temp = inp>>int(length-location)
        finval = (finval + (temp&1))<<1
    return (finval>>1)


def shrink(inp, sbox):
    output = 0
    for i in range (0,8):
        sixbits = inp&63 #only take last 6 bits
        inp = inp>>6 #eliminate bits already taken
        row = ((sixbits>>5)*2) + (sixbits&1)
        col = ((sixbits&30)>>1) #30 is for 011110 so only middle bits are taken
        output+= (sbox[row*16+col])<<(i*4)
    return output

def encrypt(plain, key):
    i = 0
    numList = list()
    finnum = 0
    #splitting to list of 8 bytes number
    for char in plain: 
        if(i>=8):
            i=0
            numList.append(finnum)
            finnum = 0
        finnum = (finnum << 8) + ord(char)
        # print(finnum)
        i+=1
    numList.append(finnum)
    CipherText = str()
    for num in numList:
        cipherTextTemp = str() #used to reverse, and add back to cipherText
        encrypted = DES(num,key)
        while(encrypted!=0):
            cipherTextTemp += chr(encrypted&255)
            encrypted = encrypted>>8
        CipherText += cipherTextTemp[::-1]
    return CipherText
    

def decrypt(ciper, key):
    i = 0
    numList = list()
    finnum = 0
    #splitting to list of 8 bytes number
    for char in ciper: 
        if(i>=8):
            i=0
            numList.append(finnum)
            finnum = 0
        finnum = (finnum << 8) + ord(char)
        i+=1
    numList.append(finnum)

    plainText = str()
    for num in numList:
        plainTextTemp = str()
        decrypted = DES(num,key)
        while(decrypted!=0):
            plainTextTemp += chr(decrypted&255)
            decrypted = decrypted>>8
        plainText += plainTextTemp[::-1]
    return plainText

def DES(number, key):
    msb = key>>55 #perfrom cyclic left shift to the 56 bits numKey
    key = ((key - (msb<<55))<<1) + msb
    subkey = permutate(key,PC2,56)# processing the subkey (48 bits)

    number = permutate(number,IP,64) #initial permutation of input number
    for dummy in range(0,16): #16 rounds
        left = number>>32
        nextLeft = right = number-(left<<32)#splitting number into 32bits halves
        right = permutate(right,EXPAND,32)

        #coming back to right side manipulation
        right = right^subkey #xor the right and 48bits subkey
        right = shrink(right,SBOX) #shrink back down to 32 bits
        right = permutate(right,P_INT,32)
        right = right^left 
        number = right + (nextLeft<<32)
    #final exchange of left and right
    left = number>>32
    right = number-(left<<32)
    number = left + (right<<32)
    finalResult = permutate(number,IP_INVERT,64)
    return finalResult