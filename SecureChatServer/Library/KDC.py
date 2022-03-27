import sys, sqlite3, json, time
from Library.Consts import *
from Library.Helpers import *

class KDC:
    con = sqlite3.connect('KDC.db')
    cur = con.cursor()
    Masterkey = -1
    
    def __init__(self):
        self.cur.execute("select * from Admin where ID=:target", {"target": "Admin"})
        self.Masterkey = self.cur.fetchone()[1]
        
    # generate a Ticket Generating Ticket for Alice to request service ticket.
    # AS for Authentication Server.
    def AS(self, request):
        self.cur.execute("select * from Users where ID=:target", {"target": request['ID']})
        requester_tuple = self.cur.fetchone()
        if (requester_tuple is None):
            return -1
        # Generate session key for TGS
        Session_Key_TGT = keyGeneration()
        # For TGS to check the session_key_TGT
        Plain_KDC_Ticket = {
            'requester_ID' : request['ID'],
            'session_key_TGT' : Session_Key_TGT
        }
        Enc_KDC_Ticket = fakeDES_Encrypt(json.dumps(Plain_KDC_Ticket), self.Masterkey)
        Plain_TGT = {
            'session_key_TGT' : Session_Key_TGT,
            'KDC_Ticket' : Enc_KDC_Ticket
        }
        # encrypt the TGT with requester's key, share the session key for TGS over.
        Enc_TGT = fakeDES_Encrypt(json.dumps(Plain_TGT), requester_tuple[1])
        return Enc_TGT
        
        
    # Authentication Server, grant Ticket Granting Ticket
    # Create S ,Compute TGT=K(key of KDC){user,S(user) Derive K(KDC) }
    # This funciton takes in a request as a dictionary.
    # TGS stands for Ticket Granting Server
    def TGS(self, request):
        self.cur.execute("select * from Users where ID=:target", {"target": request['ID']})
        requester_tuple = self.cur.fetchone()
        self.cur.execute("select * from Users where ID=:target", {"target": request['Target']})
        target_tuple = self.cur.fetchone()
        # error checking, ensure we have the target and requester in database.
        if ((requester_tuple is None) or (target_tuple is None)):
            return -1
        # Generate session key between Requester and Target
        Req_Targ_Key = keyGeneration()
        # get the timestamp for the session key.
        timestamp = time.time()
        TargetTicket = {
            'requester_ID' : requester_tuple[0],
            'session_key' : Req_Targ_Key,
            'timestamp' : timestamp,
            'lifetime' : SESSION_LENGTH
        }
        # use \n to separate between requester ID and the session key.
        encrypted_TargetTicket = fakeDES_Encrypt(json.dumps(TargetTicket), target_tuple[1])
        RequesterTicket = {
            'target_ID' : target_tuple[0],
            'session_key' : Req_Targ_Key,
            'TargetTicket' : encrypted_TargetTicket,
            'timestamp' : timestamp,
            'lifetime' : SESSION_LENGTH
        }
        encrypted_RequesterTicket = fakeDES_Encrypt(json.dumps(RequesterTicket), requester_tuple[1])
        return encrypted_RequesterTicket
        