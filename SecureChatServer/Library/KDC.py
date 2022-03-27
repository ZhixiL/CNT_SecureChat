import sys, sqlite3
from datetime import datetime
from Library.Consts import *
from Library.Helpers import *

def fakeDES(message, key):
    return message

class KDC:
    con = sqlite3.connect('KDC.db')
    cur = con.cursor()
    Masterkey = -1
    
    def __init__(self):
        self.cur.execute("select * from Users where ID=:target", {"target": "Master"})
        self.Masterkey = self.cur.fetchone()[2]
        
    # Authentication Server, grant Ticket Granting Ticket with user's password.
    # Create S ,Compute TGT=K(key of KDC){user,S(user) Derive K(KDC) }
    # This funciton takes in a request as a dictionary.
    def TicketGeneration(self, request):
        self.cur.execute("select * from Users where ID=:target", {"target": request['ID']})
        requester_tuple = self.cur.fetchone()
        # Check if the password matches from the requester.
        if (requester_tuple[1] != request['Password']):
            return -1
        self.cur.execute("select * from Users where ID=:target", {"target": request['Target']})
        target_tuple = self.cur.fetchone()
        # Generate session key between Requester and Target
        Req_Targ_Key = keyGeneration()
        # use \n to separate between requester ID and the session key.
        TargetTicket = fakeDES(f"{requester_tuple[0]}\n{Req_Targ_Key}", target_tuple[2])
        RequesterTicket = fakeDES(f"{Req_Targ_Key}\n{TargetTicket}", requester_tuple[2])
        return RequesterTicket