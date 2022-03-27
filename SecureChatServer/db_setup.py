# Sets up the SQLite3 Database
# Function - Establish Database for testing purpose.
import sqlite3, datetime, time, sys, os
from Library.Helpers import keyGeneration

con = sqlite3.connect('KDC.db')
# Create cursor object that can execute database commands.
cur = con.cursor()

# Create table, Only KDC will have access to this database.
cur.execute('''CREATE TABLE IF NOT EXISTS Users
            (ID text, key integer)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Admin
            (ID text, key integer, password text)''')

user_list = [
    ("Alice", keyGeneration()),
    ("Zack", keyGeneration()),
    ("Bob", keyGeneration())
]
admin_list = [
    ("Admin", keyGeneration(), "AdminPass")
]

cur.executemany("insert into Users values (?, ?)", user_list)
cur.executemany("insert into Admin values (?, ?, ?)", admin_list)

cur.execute("select * from Users")
print(cur.fetchall())
cur.execute("select * from Admin")
print(cur.fetchall())

con.commit()
con.close()