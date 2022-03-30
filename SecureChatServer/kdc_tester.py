from Library.KDC import *
from Library.Helpers import *
from Library.Trip_DES import encrypt, decrypt
import json, time

KDC_Server = KDC()
AlicePrivateKey = '42320678637539494109569624366015020065640581013633316606800'
BobPrivateKey = '31714869210283668071929826143654302196254149438589351184228'

asRequest = {
    "ID" : "Alice"
}
tgt = KDC_Server.AS(asRequest)
# print(f"Encrypted TGT: {tgt}") # not printable
# Using Alice's private key to decrypt, then convert it back to dictionary.
dec_tgt = json.loads(decrypt(tgt, AlicePrivateKey))
print(f"\nDecrypted TGT: {dec_tgt}")

tgsRequest = {
    "ID" : "Alice",
    "Target" : "Bob",
    "TGT" : dec_tgt['KDC_Ticket'],
    "auth" : encrypt(str(time.time()), dec_tgt['session_key_TGT'])
}
print(f"\ntgs Request:{tgsRequest}")

# get the ticket from TGS
enc_response = KDC_Server.TGS(tgsRequest)
# print(f"\nEncrypted TGS response ticket: {enc_response}") # not printable
if enc_response != -1:
    req_ticket = decrypt(enc_response, dec_tgt['session_key_TGT'])
    plain_ticket = json.loads(str(req_ticket)) #convert back to a dictionary
    print(f"\nDecrypted TGS response ticket: {plain_ticket}")
    tar_tic = json.loads(decrypt(plain_ticket['TargetTicket'], BobPrivateKey))
    print(f"\nDecrypted Target Ticket with Target's private key {tar_tic}")