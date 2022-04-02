import socket
import select
import errno
import hashlib, uuid
from getpass import getpass
import sys

#5. Algorithm in client side to handle KDC Request and Response - Jordan
     #5.5. ~ensure user messages update upon each send

#2. Find out how exactly client side needs to interact with KDC

# Notes from Zack for KDC client side implementation:
# Make Sure the message sent is in json dumped Dictionary Form, check server.py to see exactly how it's decoded.
# Here's the sequence of how KDC AS should work (for detail refer to lecture notes):
#   1. User end sends AS request to server, where server will send back a message with TGT
#   2. User end decrypts TGT, obtain the session_key_TGT (check for expiration). Now user is capable of request tickets.
# And this is how Ticket request should work:
#   1. User end sends TGS request to server, where server will send back a message with Ticket that can be decrypted with session_key_TGT
#   2. User uses the session_key_TGT to decrypt message (this has to be decoded with json of course), now user can send it over to target to initialize a session.

LENGTH = 32

IP = "127.0.0.1"
PORT = 9876
my_username = input("Username: ")
my_password = getpass()
#need to have password "silently" entered


#Have a registered list of names in KDC master database?
#check against what to determine if KDC recognizes the user
#How do we send user messages to KDC? How is it accessed? In an offline manner?
#Need password to authenticate users??
#need to be able to pass password and other system things from this client.py to the KDC function in some way

# Create a socket
cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
cli.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
cli.setblocking(False)

# Prepare username and header and send them
# We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
username = my_username.encode('utf-8')
username_header = f"{len(username):<{LENGTH}}".encode('utf-8')

password = bytes(my_password, 'utf-8')
#password_header = f"{len(password):<{LENGTH}}".encode('utf-8')
salt = bytes(uuid.uuid4().hex, 'utf-8')
hashed_password = hashlib.sha512(password + salt).hexdigest()
#need to send hashed_password to KDC somehow
cli.send(username_header + username)

while True:

    # Wait for user to input a message
    message = input(f'{my_username} > ')

    # If message is not empty - send it
    if message:

        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
        message = message.encode('utf-8')
        message_header = f"{len(message):<{LENGTH}}".encode('utf-8')
        cli.send(message_header + message)

    try:
        # Loop over received messages and print them
        while True:

            # Receive our "header" containing username length
            username_header = cli.recv(LENGTH)

            # If we received no data, connection was closed
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            # Convert header to int value
            username_length = int(username_header.decode('utf-8').strip())

            # Receive and decode username
            username = cli.recv(username_length).decode('utf-8')

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