KEY_LENGTH = 196
SESSION_LENGTH = 30  # seconds, temporary set to 30 for testing purpose.
TGT_SESSION_LENGTH = 120  # seconds
AUTH_TIME = 1  # seconds, make sure diff of sending Ticket Request and Receiving Request < AUTH_TIME

# 2**DH_KEY_LENGTH for DH private key, g, and 2**(DH_KEY_LENGTH+1) for p (p has to be larger than g)
# DH_KEY_LENGTH = 128 

RSA_KEY_LENGTH = 1024

# SERVER.PY
LENGTH = 128  # Length of the header, stores the length of message.
IP = "127.0.0.1"
PORT = 9876
