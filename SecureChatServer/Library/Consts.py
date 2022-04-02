KEY_LENGTH = 196
SESSION_LENGTH = 30 # seconds, temporary set to 30 for testing purpose.
TGT_SESSION_LENGTH = 120 # seconds
AUTH_TIME = 1 # seconds, make sure diff of sending Ticket Request and Reciving Request < AUTH_TIME

# SERVER.PY
LENGTH = 32 # sets the message header length 
IP = "127.0.0.1"
PORT = 9876