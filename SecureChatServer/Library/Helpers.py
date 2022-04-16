import random, sqlite3, json
from Library.Consts import *

def keyGeneration():
    return str(random.randint(0, 2**KEY_LENGTH))

def getIntKey(input):
    return int(input)

# You can use this in the client side, just make sure to use this appropriately
# with correct cursor object and target name, and there exist Users column in your .db
def checkExist(cur, name):
    if isinstance(cur, sqlite3.Cursor):
        cur.execute("select * from Users where ID=:target", {"target": name})
        if cur.fetchone() is None:
            return False
        else:
            return True
    else:
        print("The first parameter inputted isn't a cursor object!")
        return False
    
# take in a dictionary, encode it with it's length as utf-8 then return it.
def encodeMessage(message):
    encoded_msg = json.dumps(message).encode('utf-8')
    # grab the length of encoded msg, pad it until length, then store it as header.
    message_header = f"{len(encoded_msg):<{LENGTH}}".encode('utf-8')
    return (message_header + encoded_msg)

def genPrime(length):
    # generate a random number that's around 2^length
    randnum = (random.randrange(2**(length-1)+1, 2**length-1))
    while (checkPrime(randnum) is False):
        randnum = (random.randrange(2**(length-1)+1, 2**length-1))

# fermat's primality test
def checkPrime(num):
    # test cases for primality test, which are all primes.
    testers = {2, 3, 5}
    #now conduct primality check
    for p in testers:
        # check if p**(num-1) % num != 1
        if powModRecur(p, num-1, num) != 1:
            return False
    return True

# Modular exponentiation that utilize multiplicative property.
def powMod(a, b, n):
    ret = 1
    for tmp in range(b):
        ret = ret * a % n
    return ret

# Recursive implementation of powMod
def powModRecur(base, power, n):
    # separate base into equal amount of left and right
    l = int(power/2)
    r = power - l
    # this is base case, where l and r are small enough to process.
    if (l < 3 or r < 3):
        return (powMod(base, l, n) * powMod(base, r, n)) % n
    # this is the recursive step where l and r still needs to be broken down.
    else:
        return (powModRecur(base, l, n) * powModRecur(base, r, n)) % n