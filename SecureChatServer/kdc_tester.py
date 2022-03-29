from Library.KDC import *
from Library.Helpers import *
import json, time

KDC_Server = KDC()
AlicePrivateKey = '42320678637539494109569624366015020065640581013633316606800'

asRequest = {
    "ID" : "Alice"
}
tgt = KDC_Server.AS(asRequest)

# Using Alice's private key to decrypt, then convert it back to dictionary.
dec_tgt = json.loads(fakeDES_Decrypt(tgt, AlicePrivateKey))
print(f"TGT: {dec_tgt}")

tgsRequest = {
    "ID" : "Alice",
    "Target" : "Bob",
    "TGT" : dec_tgt['KDC_Ticket'],
    "auth" : fakeDES_Encrypt(str(time.time()), dec_tgt['session_key_TGT'])
}

# get the ticket from TGS
enc_response = KDC_Server.TGS(tgsRequest)
if enc_response != -1:
    req_ticket = fakeDES_Decrypt(enc_response, dec_tgt['session_key_TGT'])
    plain_ticket = json.loads(str(req_ticket)) #convert back to a dictionary
    print(f"requester ticket: {plain_ticket}")
    tar_tic = json.loads(plain_ticket['TargetTicket'])
    print(f"target ticket {tar_tic}")