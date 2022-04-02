import random, sqlite3
from Library.Consts import *

def keyGeneration():
    return str(random.randint(0, 2**KEY_LENGTH))

def getIntKey(input):
    return int(input)

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