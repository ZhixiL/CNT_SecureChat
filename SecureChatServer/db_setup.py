# Sets up the SQLite3 Database
# Function - Establish Database for testing purpose.
import sqlite3
from Library.Helpers import keyGeneration

con = sqlite3.connect('KDC.db')
# Create cursor object that can execute database commands.
cur = con.cursor()

# Create table, Only KDC will have access to this database.
# Prevent multiple creation of user/admin.
cur.execute('''CREATE TABLE Users
            (ID text, key text, password text)''')

cur.execute('''CREATE TABLE Admin
            (ID text, key text, password text)''')

# cur.execute('''Create Table if not exists TGTs 
#             (ID text, key text, timestamp integer)''')

user_list = [
    ("Alice", keyGeneration(), "alicepass"),
    ("Zack", keyGeneration(), "zackpass"),
    ("Bob", keyGeneration(), "bobpass")
]
admin_list = [
    ("Admin", keyGeneration(), "AdminPass")
]

cur.executemany("insert into Users values (?, ?, ?)", user_list)
cur.executemany("insert into Admin values (?, ?, ?)", admin_list)

cur.execute("select * from Users")
print(cur.fetchall())
cur.execute("select * from Admin")
print(cur.fetchall())

con.commit()
con.close()