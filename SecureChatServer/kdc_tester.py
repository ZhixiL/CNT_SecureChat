from Library.KDC import *
from Library.Helpers import *
import json

KDC_Server = KDC()

asRequest = {
    "ID" : "Alice"
}

tgt = KDC_Server.AS(asRequest)
# Using Alice's private key to decrypt, then convert it back to dictionary.
dec_tgt = json.loads(fakeDES_Decrypt(tgt, 21107429551728165))
print(f"TGT: {dec_tgt}")

tgsRequest = {
    "ID" : "Alice",
    "Password" : "AlicePass",
    "Target" : "Bob",
    "TGT" : dec_tgt['KDC_Ticket']
}

req_ticket = fakeDES_Decrypt(KDC_Server.TGS(tgsRequest), dec_tgt['session_key_TGT'])
req_ticket = (json.loads(req_ticket))
print(f"requester ticket: {req_ticket}")
tar_tic = json.loads(req_ticket['TargetTicket'])
print(f"target ticket {tar_tic}")
