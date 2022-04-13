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
    while (checkPrime(randnum)):
        randnum = (random.randrange(2**(length-1)+1, 2**length-1))

# still implementing...
def checkPrime(num):
    return 0
