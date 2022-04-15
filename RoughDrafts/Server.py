import socket, select, sqlite3, json
from time import sleep
from urllib import request
from Library.Consts import *
from Library.Helpers import *
from Library.KDC import KDC
from Library.DH import DH

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

        # separate the  header from the actual message and return
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:

        # This only happens in case of a closed or lost connection
        return False
        

while True:
    # call to select to see if we received messages or generated exceptions 
    # on connected sockets.  
    read_sockets, dummy, exception_sockets = select.select(sockets_list, [], sockets_list)

    sleep(0.1)
    # Iterate over sockets that sent messages
    for notified_socket in read_sockets:

        # If the socket is the server it's a new connection, accept it
        if notified_socket == serv:

            # Accept new connection
            client_socket, client_address = serv.accept()
            print(f" client socket -> {client_socket}")

            # Grab the user's name
            user = receive_message(client_socket)
            
            # If False - client disconnected before first message
            if user is False:
                continue

            # WARNING: if you need to test new users modify this part, otherwise server won't take new user requets.
            if checkExist(cur, user['data'].decode('utf-8')) is True:
                # only add accepted socket to the list and the dictionary when the user exist.
                sockets_list.append(client_socket)
                clients[client_socket] = user
                print('Accepted connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
                

        # If existing socket is sending a message
        # !!! Make Sure To Send Message in json dumped Dictionary Form! !!!
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
            print(msgDict)
            
            user = clients[notified_socket]
            
            # For message without a target, meaning that it's a request for TGT or Ticket, thus conduct the following then send the requested item back to user.
            if msgDict.get('Target') is None:
                # Take in the request from user that requests for TGT or 
                if msgDict.get('AS') is not None:
                    print(f"AS request from {user['data'].decode('utf-8')}. ")
                    ret['TGT'] = KDCServer.AS(msgDict['AS'])
                    ret['msg'] = "AS-request successful..."
                    cur.execute("SELECT key FROM Users WHERE ID =?", (f"{user['data'].decode('utf-8')}",))
                    #print(cur.fetchall())
                    pKey = cur.fetchone()
                    pKey = ''.join(pKey)
                    print(pKey)
                    ret['key'] = pKey
                elif msgDict.get('TGS') is not None:
                    print(f"TGS request from {user['data'].decode('utf-8')}. ")
                    ret['Ticket'] = KDCServer.TGS(msgDict['TGS'])
                    ret['msg'] = "TGS Request..."
                
                # Iterate over other clients and broadcast the message
                for client_socket in clients:
                    # Sends the TGT/Ticket back to client with message.
                    if client_socket == notified_socket:
                        client_socket.send(encodeMessage(ret))
            
            # If there exist target, redirect message to target:
            # Secure session is established on the basis that both clients have a shared key, so it doesn't has to be done on the server-end explicitly.
            else:
                for client_socket in clients:
                    # Sends the ticket/encrypted msg to target client.
                    if client_socket['data'].decode('utf-8') == msgDict['Target']:
                        client_socket.send(encodeMessage(msgDict))
                        print("sent message to other client")
                        print(f"msg -> {msgDict}")
                
                
                

    # Handle some socket exceptions just in case
    for notified_socket in exception_sockets:
        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)
        # Remove from our list of users
        del clients[notified_socket]

