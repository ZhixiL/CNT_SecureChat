from Library.KDC import *
from Library.Helpers import *
from Library.Trip_DES import encrypt, decrypt
import json, time

KDC_Server = KDC()
AlicePrivateKey = '81013256490707796504331405112674572312863443534940776625515'
BobPrivateKey = '2362942845227432155159665180189153733280174805612295017510'

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
    # print(f"\nEncrypted TGS response ticket: {enc_response}")
    req_ticket = decrypt(enc_response, dec_tgt['session_key_TGT'])
    plain_ticket = json.loads(str(req_ticket)) #convert back to a dictionary
    print(f"\nDecrypted TGS response ticket: {plain_ticket}")
    tar_tic = json.loads(decrypt(plain_ticket['TargetTicket'], BobPrivateKey))
    print(f"\nDecrypted Target Ticket with Target's private key {tar_tic}")