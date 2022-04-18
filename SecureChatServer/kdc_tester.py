from Library.KDC import *
from Library.Trip_DES import encrypt, decrypt
import json, time

KDC_Server = KDC()
AlicePrivateKey = '51412044808051795446591339911130555190904197455176087957727'
BobPrivateKey = '52843837072175168347280920510069729346951168685240858757426'

asRequest = {
    "ID": "Alice"
}
tgt = KDC_Server.AS(asRequest)
# print(f"Encrypted TGT: {tgt}") # not printable
# Using Alice's private key to decrypt, then convert it back to dictionary.
dec_tgt = json.loads(decrypt(tgt, AlicePrivateKey))
print(f"\nDecrypted TGT: {dec_tgt}")

tgsRequest = {
    "ID": "Alice",
    "Target": "Bob",
    "TGT": dec_tgt['KDC_Ticket'],
    "auth": encrypt(str(time.time()), dec_tgt['session_key_TGT'])
}
print(f"\ntgs Request:{tgsRequest}")

# Get the ticket from TGS
enc_response = KDC_Server.TGS(tgsRequest)
# print(f"\nEncrypted TGS response ticket: {enc_response}") # not printable
if enc_response != -1:
    # print(f"\nEncrypted TGS response ticket: {enc_response}")
    req_ticket = decrypt(enc_response, dec_tgt['session_key_TGT'])
    plain_ticket = json.loads(str(req_ticket))  # Convert back to a dictionary
    print(f"\nDecrypted TGS response ticket: {plain_ticket}")
    tar_tic = json.loads(decrypt(plain_ticket['TargetTicket'], BobPrivateKey))
    print(f"\nDecrypted Target Ticket with Target's private key {tar_tic}")