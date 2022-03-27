# Sets up the SQLite3 Database
# Function - Establish Database for testing purpose.
import sqlite3, datetime, time, sys, os
from Library.Helpers import keyGeneration

con = sqlite3.connect('KDC.db')
# Create cursor object that can execute database commands.
cur = con.cursor()

# Create table, Only KDC will have access to this database.
cur.execute('''CREATE TABLE IF NOT EXISTS Users
            (ID text, password text, key integer)''')

user_list = [
    ("Master", "MasterPass", keyGeneration()),
    ("Alice", "AlicePass", keyGeneration()),
    ("Zack", "ZackPass", keyGeneration()),
    ("Bob", "BobPass", keyGeneration())
]

cur.executemany("insert into Users values (?, ?, ?)", user_list)

cur.execute("select * from Users")
print(cur.fetchall())

con.commit()
con.close()