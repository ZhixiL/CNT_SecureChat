#from re import M
import socket, select, errno
import hashlib, uuid
from getpass import getpass
import sys, json, time

step = 0
AS_RequestComplete = False
TGS_RequestComplete = False

# These imports are temporary, when the user-end is ready to be deployed independently, following files should be moved to current directory's Library.
from Consts import *
from Trip_DES import encrypt, decrypt
BobPrivateKey = 59555794708254095491281016864256854649705243541885733613115
#Private key will be local database dependent

# Create a socket
cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
cli.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
cli.setblocking(False)

my_username = input("Username: ")
my_password = getpass()
#need to have password "silently" entered // will need the password of a user to verify at some point?
#msgRequest = input(f'Who would you like to speak to? > ') #temporary so I know who user wants to speak with


# Prepare username and header and send them
# We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
username = my_username.encode('utf-8')
message_header = f"{len(username):<{LENGTH}}".encode('utf-8')
cli.send(message_header + username) #Hello, my name is Alice

# password = bytes(my_password, 'utf-8')
# #password_header = f"{len(password):<{LENGTH}}".encode('utf-8')
# salt = bytes(uuid.uuid4().hex, 'utf-8')
# hashed_password = hashlib.sha512(password + salt).hexdigest()

KDC_AS_Setup = {
    "ID" : f"{my_username}", 
    "AS" :{
        "ID" : f"{my_username}"
    }
}




#print(f'Now we want to setup the KDC so {my_username} can speak to {msgRequest} ')   

asRequest = json.dumps(KDC_AS_Setup).encode('utf-8')
asHeader = f"{len(asRequest):<{LENGTH}}".encode('utf-8')
cli.send(asHeader + asRequest)




########################################################33

while step != 1: #change to 2 for full configuration

    try:
        # Loop over received messages and print them
        while True:            
            # Receive our "header" containing ticket length
            ticket_header = cli.recv(LENGTH)

            # If we received no data, connection was closed
            if not len(ticket_header):
                print('Connection closed by the server')
                sys.exit()

            # Convert header to int value
            ticket_length = int(ticket_header.decode('utf-8').strip())

            # Receive and decode ticket
            returned_msg = cli.recv(ticket_length).decode('utf-8')
            returned_dict = json.loads(returned_msg) #change ticket to returned message
        

            # Print message
            print(f'KDC Message > {returned_msg}')
            step = step + 1
            

    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        continue

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: '.format(str(e)))
        sys.exit()

dec_tgt = decrypt(returned_dict['TGT'], BobPrivateKey)
print(dec_tgt)
tgt = json.loads(dec_tgt)
KDC_TGS_Setup = {
    "ID" : f"{my_username}",
    "TGS" :{
        "ID" : f"{my_username}",
        "Target" : "Alice",
        "TGT" : tgt['KDC_Ticket'],
        "auth" : encrypt(str(time.time()), tgt['session_key_TGT'])
    }
}

tgsRequest = json.dumps(KDC_TGS_Setup).encode('utf-8')
tgsHeader = f"{len(tgsRequest):<{LENGTH}}".encode('utf-8')
cli.send(tgsHeader + tgsRequest)



##################################################################################################3



while True:

    # Wait for user to input a message
    message = input(f'{my_username} > ') #Let me speak to someone


    #user is going to have to state who they wanna talk to, then we can handle server request
    #in the backhround and make a kdc request to the particular user they want if they are valid

    # If message is not empty - send it
    if message:

        ### From Zack: For our implementation purpose, we'll use a json-based dictionary only for message, thus the plain-text will be abandoned.###
        ### For example, json.dumps the message then encode it with utf-8. Server will decode it then use json.loads to unpack it. ###
        
        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
        message = message.encode('utf-8')
        message_header = f"{len(message):<{LENGTH}}".encode('utf-8')
        cli.send(message_header + message)

    try:
        # Loop over received messages and print them
        while True:
            
            # Receive our "header" containing username length
            message_header = cli.recv(LENGTH)

            # If we received no data, connection was closed
            if not len(message_header):
                print('Connection closed by the server')
                sys.exit()

            # Convert header to int value
            message_length = int(message_header.decode('utf-8').strip())

            # Receive and decode username
            username = cli.recv(message_length).decode('utf-8')

            # Now do the same for message
            message_header = cli.recv(LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = cli.recv(message_length).decode('utf-8')

            # Print message
            print(f'{username} > {message}')

    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        continue

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: '.format(str(e)))
        sys.exit()

# Notes from Zack for KDC client side implementation:
# Make Sure the message sent is in json dumped Dictionary Form, check server.py to see exactly how it's decoded.
# Here's the sequence of how KDC AS should work (for detail refer to lecture notes):
#   1. User end sends AS request to server, where server will send back a message with TGT
#   2. User end decrypts TGT, obtain the session_key_TGT (check for expiration). Now user is capable of request tickets.
# And this is how Ticket request should work:
#   1. User end sends TGS request to server, where server will send back a message with Ticket that can be decrypted with session_key_TGT
#   2. User uses the session_key_TGT to decrypt message (this has to be decoded with json of course), now user can send it over to target to initialize a session.
