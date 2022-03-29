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
        timestamp = time.time()
        # self.cur.execute("insert into TGTs values (?, ?, ?)", (request['ID'], Session_Key_TGT, timestamp))
        # For TGS to check the session_key_TGT
        Plain_KDC_Ticket = {
            'requester_ID' : request['ID'],
            'session_key_TGT' : Session_Key_TGT,
            'timestamp' : timestamp,
            'lifetime' : TGT_SESSION_LENGTH
        }
        Enc_KDC_Ticket = fakeDES_Encrypt(json.dumps(Plain_KDC_Ticket), self.Masterkey)
        Plain_TGT = {
            'session_key_TGT' : Session_Key_TGT,
            'KDC_Ticket' : Enc_KDC_Ticket,
            'timestamp' : timestamp,
            'lifetime' : TGT_SESSION_LENGTH
        }
        # encrypt the TGT with requester's key, share the session key for TGS over.
        Enc_TGT = fakeDES_Encrypt(json.dumps(Plain_TGT), requester_tuple[1])
        return Enc_TGT
        
        
    # Authentication Server, grant Ticket Granting Ticket
    # Create S ,Compute TGT=K(key of KDC){user,S(user) Derive K(KDC) }
    # This funciton takes in a request as a dictionary.
    # TGS stands for Ticket Granting Server
    def TGS(self, request):
        Plain_TGT = json.loads(fakeDES_Decrypt(request['TGT'], self.Masterkey))
        if (request['ID'] != Plain_TGT['requester_ID']):
            print("ERROR: ID doesn't Match...")
            return -1
        if (Plain_TGT['timestamp']+Plain_TGT['lifetime'] < time.time()):
            print("ERROR: This TGT has expired...")
            return -1
        if (time.time() - float(fakeDES_Decrypt(request['auth'], Plain_TGT['session_key_TGT'])) > AUTH_TIME):
            print(f"DANGER: AUTH_TIME {AUTH_TIME}s exceeded, request may be intercepted!")
            return -1
        
        self.cur.execute("select * from Users where ID=:target", {"target": request['ID']})
        requester_tuple = self.cur.fetchone()
        self.cur.execute("select * from Users where ID=:target", {"target": request['Target']})
        target_tuple = self.cur.fetchone()
        # error checking, ensure we have the target and requester in database.
        if ((target_tuple is None)):
            print(f"ERROR: Target ({request['Target']}) Doesn't exist.")
            return -1
        # Generate session key between Requester and Target
        Req_Targ_Key = keyGeneration()
        # get the timestamp for the session key.
        timestamp = time.time()
        TargetTicket = {
            'requester_ID' : request['ID'],
            'session_key' : Req_Targ_Key,
            'timestamp' : timestamp,
            'lifetime' : SESSION_LENGTH
        }
        # use \n to separate between requester ID and the session key.
        encrypted_TargetTicket = fakeDES_Encrypt(json.dumps(TargetTicket), target_tuple[1])
        RequesterTicket = {
            'target_ID' : target_tuple[0],
            'session_key' : Req_Targ_Key, # Requester and Target Symmetric Key
            'TargetTicket' : encrypted_TargetTicket,
            'timestamp' : timestamp,
            'lifetime' : SESSION_LENGTH
        }
        encrypted_RequesterTicket = fakeDES_Encrypt(json.dumps(RequesterTicket), Plain_TGT['session_key_TGT'])
        return encrypted_RequesterTicket
        