from ast import Not
import socket, select, sqlite3, json, rsa
from time import sleep
from Library.Consts import *
from Library.Helpers import *
from Library.KDC import KDC

con = sqlite3.connect('KDC.db')
cur = con.cursor()
KDCServer = KDC()

# Create a socket - INET, STREAM, like we did in class
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# We can set socket options. Here, we set REUSEADDR to 1
# More info: https://manpages.debian.org/buster/manpages-dev/setsockopt.2.en.html
serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the chosen IP address and port number
serv.bind((IP, PORT))

# Now, listen for incoming connections on that IP address and port
serv.listen()

# Add all the connected sockets to a list. select() will use it later
# Add the server socket to the list
sockets_list = [serv]

# Maintain a dictionary of connected clients 
clients = {}

# generate an public/private key pair for current session
# for KDC private key exchange purpose.
(pubkey, privkey) = rsa.newkeys(RSA_KEY_LENGTH)

print('Listening on ', IP, PORT)

# Define actions when a message is received
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(LENGTH)
        # If we reveived no data, client has closed the connection
        if not len(message_header):
            return False
        
        # calculate actual length to extract the message.
        message_length = int(message_header.decode('utf-8').strip())
        if message_length == 0:
            return False

        # separate the  header from the actual message and return
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:

        # This only happens in case of a closed or lost connection
        return False
        
newUserFlag = False
while True:
    # call to select to see if we received messages or generated exceptions 
    # on connected sockets.  
    read_sockets, dummy, exception_sockets = select.select(sockets_list, [], sockets_list)

    # Iterate over sockets that sent messages
    for notified_socket in read_sockets:

        # If the socket is the server it's a new connection, accept it
        if notified_socket == serv:

            # Accept new connection
            client_socket, client_address = serv.accept()

            # Grab the user's name
            user = receive_message(client_socket)
            
            # If False - client disconnected before first message
            if user:
                if checkExist(cur, user['data'].decode('utf-8')) is False:
                    newUserFlag = True
                    print("This is a new user...")
                else:
                    newUserFlag = False
                sockets_list.append(client_socket)
                clients[client_socket] = user
                print('Accepted connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
            

        # If existing socket is sending a message
        else:
            # Receive message
            message = receive_message(notified_socket)
            # initiate a return dictionary
            ret = {}

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                # Remove from list and dictionary
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
                
            # unpack the message to dictionary
            msgDict = json.loads(message["data"].decode("utf-8"))
            
            user = clients[notified_socket]
            
            
            # For message without a target, meaning that it's a server request
            if msgDict.get('Target') is None:
                # RSA Authentication Part
                if msgDict.get('RSA_PublicKeyRequest') is not None:
                    ret['pubkey_e'] = pubkey.e
                    ret['pubkey_n'] = pubkey.n
                
                elif msgDict.get('RSA_Request_KDC_PrivKey') is not None:
                    requester = msgDict['ID']
                    requester_pubkey = rsa.PublicKey(msgDict['requester_pubkey_n'], msgDict['requester_pubkey_e'])
                    EncPswd = msgDict['EncPswd'].to_bytes(msgDict['PswdLen'], byteorder='big')
                    pswd = rsa.decrypt(EncPswd, privkey).decode('utf-8')
                    requester_tuple = tuple()
                    if newUserFlag: # Registration
                        print("This is a new user")
                        requester_tuple = (msgDict['ID'], keyGeneration(), pswd)
                        cur.execute("insert into Users values (?, ?, ?)", requester_tuple)
                        con.commit()
                    else: # Existing User Log-in
                        cur.execute("select * from Users where ID=:target", {"target": requester})
                        requester_tuple = cur.fetchone()
                    if requester_tuple[2] == pswd:
                        print(requester_tuple[1])
                        EncPrivkey = rsa.encrypt(requester_tuple[1].encode('utf-8'), requester_pubkey)
                        print(f"encPrivKey {EncPrivkey}")
                        ret['KDC_prikey'] = int.from_bytes(EncPrivkey, "big")
                        ret['EncLen'] = len(EncPrivkey)
                        if newUserFlag:
                            ret['msg'] = "Registration successful!"
                        else:
                            ret['msg'] = "Password succesfully authenticated, KDC_prikey is returned."
                        ret['status'] = True
                    else:
                        ret['msg'] = "Password is incorrect!"
                        ret['status'] = False
                
                # KDC Part
                # Take in the request from user that requests for TGT or 
                elif msgDict.get('AS') is not None:
                    print(f"AS request from {user['data'].decode('utf-8')}. ")
                    ret['TGT'] = KDCServer.AS(msgDict['AS'])
                    ret['msg'] = "AS-request successful..."
                    ret['status'] = False if ret['TGT'] == -1 else True
                        
                    
                elif msgDict.get('TGS') is not None:
                    print(f"TGS request from {user['data'].decode('utf-8')}. ")
                    ret['Ticket'] = KDCServer.TGS(msgDict['TGS'])
                    ret['msg'] = "TGS Request Complete..."
                    ret['status'] = False if ret['Ticket'] == -1 else True
                
                for client_socket in clients:
                    # Sends the TGT/Ticket back to client with message.
                    if client_socket == notified_socket:
                        # print(f"server request is responded with the following:\n{ret}")
                        # print(f"length is {len(json.dumps(ret))}")
                        client_socket.send(encodeMessage(ret))
            
            # Bypass message to the client.
            # If there exist target, redirect message to target:
            # Secure session is established on the basis that both clients have a shared key, so it doesn't has to be done on the server-end explicitly.
            else:
                status = False
                print(notified_socket)
                for client_socket in clients:
                    # Sends the ticket/encrypted msg to target client.
                    if clients[client_socket]['data'].decode('utf-8') == msgDict['Target']:
                        client_socket.send(encodeMessage(msgDict))
                        status = True
                if status is False:
                    # sends the false status back to the client, where client should display this message to the user.
                    ret['status'] = False
                    ret['msg'] = "Your message/ticket is failed to deliver as the target is no longer online/exist."
                    for client_socket in clients:
                        # Sends the false message back to user.
                        if client_socket == notified_socket:
                            client_socket.send(encodeMessage(ret))
                        
                        
                
                
                

    # Handle some socket exceptions just in case
    for notified_socket in exception_sockets:
        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)
        # Remove from our list of users
        del clients[notified_socket]

