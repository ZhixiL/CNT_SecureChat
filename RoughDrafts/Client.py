#from re import M
import socket, select, errno
import hashlib, uuid
from getpass import getpass
import sys, json, time

# These imports are temporary, when the user-end is ready to be deployed independently, following files should be moved to current directory's Library.
from Consts import *
from Trip_DES import encrypt, decrypt
#BobPrivateKey = 59555794708254095491281016864256854649705243541885733613115
#Private key will be local database dependent


# Create a socket
cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
cli.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
cli.setblocking(False)

sockets_list = {IP, PORT}
#make dictionary to hold connected clients

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(LENGTH)
        # If we reveived no data, client has closed the connection
        if not len(message_header):
            return False
        
        # calculate actual length to extract the message.
        message_length = int(message_header.decode('utf-8').strip())

        # separate the  header from the actual message and return
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:

        # This only happens in case of a closed or lost connection
        #return False
        return {'header' : "nothing"} #just a test

my_username = input("Username: ")
#my_password = getpass()
#need to have password "silently" entered // will need the password of a user to verify at some point?
msgRequest = input(f'Who would you like to speak to? > ') #temporary so I know who user wants to speak with

KDC_AS_Setup = {
    "ID" : f"{my_username}", 
    "AS" :{
        "ID" : f"{my_username}"
    }
}

Temp_Key_Dict = {} #will add key pair once a connection is established.. Username : Key

print(f'Now we want to setup the KDC so {my_username} can speak to {msgRequest} ')  

asRequest = json.dumps(KDC_AS_Setup).encode('utf-8')
asHeader = f"{len(asRequest):<{LENGTH}}".encode('utf-8')
cli.send(asHeader + asRequest)
#we sent something so now we need to be always listening
#Need to recieve key and TGT stuff from server somewhere here or above
while True: #want to process messages from the server first
        try:

        #Need to add a check here so it does't always run to exception
            message_header = cli.recv(LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            KDC_json = cli.recv(message_length).decode('utf-8')
            KDC_reply = json.loads(KDC_json) #add decode here?
            print("Did you reach here1?")

            print(KDC_reply)
            if(KDC_reply.get('Target') is None):

                #decrypt ticket with private key, place session key in temp dict
                if(KDC_reply.get('TGT') is not None):
                    #TGT has been sent to client?
                    returned_dict = json.loads(KDC_reply)
                    dec_tgt = decrypt(returned_dict['TGT'], returned_dict['key'])
                    print(dec_tgt)
                    tgt = json.loads(dec_tgt)
                    KDC_TGS_Setup = {
                        "ID" : f"{my_username}",
                        "TGS" :{
                            "ID" : f"{my_username}",
                            "Target" : f"{msgRequest}",
                            "TGT" : tgt['KDC_Ticket'], 
                            "auth" : encrypt(str(time.time()), tgt['session_key_TGT'])
                        }
                    }
                    

                    tgsRequest = json.dumps(KDC_TGS_Setup).encode('utf-8')
                    tgsHeader = f"{len(tgsRequest):<{LENGTH}}".encode('utf-8')
                    cli.send(tgsHeader + tgsRequest)
                elif(KDC_reply.get('Ticket') is not None):
                    #Ticket has been sent to client?
                    enc_response = KDC_reply
                    if enc_response != -1:

                        req_ticket = decrypt(enc_response, dec_tgt['session_key_TGT'])
                        plain_ticket = json.loads(str(req_ticket)).encode('utf-8')

                        Temp_Key_Dict[f'{msgRequest}' ] = dec_tgt['session_key_TGT']

                        pt_header = f"{len(plain_ticket):<{LENGTH}}".encode('utf-8')
                        cli.send(pt_header + plain_ticket)
                        #Need a dictionary to send ticket and message?
                        #target_ticket = json.loads(decrypt(plain_ticket['TargetTicket'], "private key hey"))
            elif (KDC_reply.get('Target') is not None):
                #we can also have users send messages now?
                enc_message = KDC_reply
                msgRecieved = decrypt(enc_message, Temp_Key_Dict[f'{msgRequest}'])
                #decrypt message using temporarily stored session key
                #Let me speak to someone
                message = input(f'{my_username} > ') 
                username = my_username.encode('utf-8')
                message_header = f"{len(username):<{LENGTH}}".encode('utf-8')
                cli.send(message_header + username) #Hello, my name is Alice

                username = (msgRecieved['ID'])
                msg = msgRecieved['msg']
                print(f"{username} > {msg}")

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



        # Prepare username and header and send them
        # We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
        

# password = bytes(my_password, 'utf-8')
# #password_header = f"{len(password):<{LENGTH}}".encode('utf-8')
# salt = bytes(uuid.uuid4().hex, 'utf-8')
# hashed_password = hashlib.sha512(password + salt).hexdigest()




# Notes from Zack for KDC client side implementation:
# Make Sure the message sent is in json dumped Dictionary Form, check server.py to see exactly how it's decoded.
# Here's the sequence of how KDC AS should work (for detail refer to lecture notes):
#   1. User end sends AS request to server, where server will send back a message with TGT
#   2. User end decrypts TGT, obtain the session_key_TGT (check for expiration). Now user is capable of request tickets.
# And this is how Ticket request should work:
#   1. User end sends TGS request to server, where server will send back a message with Ticket that can be decrypted with session_key_TGT
#   2. User uses the session_key_TGT to decrypt message (this has to be decoded with json of course), now user can send it over to target to initialize a session
