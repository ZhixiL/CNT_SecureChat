import socket, select, sqlite3, json
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

print('Listening on ', IP, PORT)

# Define actions when a message is received
def receive_message(client_socket):
    try:
        # We've set the length to 32. We can change it
        message_header = client_socket.recv(LENGTH)

        # If we reveived no data, client has closed the connection
        if not len(message_header):
            return False

        # COtherwise, calculate actual length
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

    # Iterate over sockets that sent messages
    for notified_socket in read_sockets:

        # If the socket is the server it's a new connection, accept it
        if notified_socket == serv:

            # Accept new connection
            client_socket, client_address = serv.accept()

            # Grab the user's name
            user = receive_message(client_socket)

            # If False - client disconnected before first message
            if user is False:
                continue

            # WARNING: if you need to test new users modify this part, otherwise server won't take new user requets.
            if checkExist(cur, user) is True:
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

            # Take in the request from user that requests for TGT or 
            if msgDict['AS'] is not None:
                ret['TGT'] = KDCServer.AS(msgDict['AS'])
            elif msgDict['TGS'] is not None:
                ret['Ticket'] = KDCServer.TGS(msgDict['AS'])

            # Get user, so we will know who sent the message
            user = clients[notified_socket]
            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # # Iterate over other clients and broadcast the message
            # for client_socket in clients:
            #     # But don't sent it to sender
            #     if client_socket != notified_socket:
            #         client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # Handle some socket exceptions just in case
    for notified_socket in exception_sockets:
        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)
        # Remove from our list of users
        del clients[notified_socket]

