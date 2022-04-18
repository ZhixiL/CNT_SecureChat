import socket, errno
import sys, json, time, rsa
import Library.GUI as GUI
from Library.Consts import *
from Library.Trip_DES import encrypt, decrypt


# Create a socket
cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
cli.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won't block
# Just return some exception we'll handle
cli.setblocking(False)

sockets_list = {IP, PORT}


# Make dictionary to hold connected clients
def sendDict(dictionary):
    encoded_dict = json.dumps(dictionary).encode('utf-8')
    # Grab the length of encoded msg, pad it until length, then store it as header.
    header = f"{len(encoded_dict):<{LENGTH}}".encode('utf-8')
    cli.send(header + encoded_dict)
    time.sleep(0.1)  # give server some time to get back...


def prep_server_pukey_request():
    return {
        'RSA_PublicKeyRequest': True
    }


def prep_RSA_auth_request(pswd):
    ret = {
        'RSA_Request_KDC_PrivKey': True,
        'requester_pubkey_e': client_pukey.e,
        'requester_pubkey_n': client_pukey.n,
        'ID': my_username
    }
    encPswd = rsa.encrypt(pswd.encode('utf-8'), serverPuKey)
    ret['EncPswd'] = int.from_bytes(encPswd, "big")
    ret['PswdLen'] = len(encPswd)
    return ret


def prep_AS_request():
    return {
        "ID": f"{my_username}",
        "AS": {
            "ID": f"{my_username}"
        }
    }


# Send get_server function... to the server
# When we get response send out prep RSA
# Wanna display error messages to clients
# Add password functionality
(client_pukey, client_privkey) = rsa.newkeys(RSA_KEY_LENGTH)
serverPuKey = 0
KDC_privkey = 0  # KDC_privkey represent user's own private key for KDC.
ActiveSessionKeys = dict()  # In the format {targetName : session key, ...}
currentTarget = None  # Save anyone that is currently chatting with.
KDC_SessionKey = None
waiting_to_be_connected = False

# Initialize the connection between user and server.
my_username = "temp"
username = my_username.strip().encode('utf-8')
username_header = f"{len(username):<{LENGTH}}".encode('utf-8')
cli.send(username_header + username)

gui = GUI.GUI()

while True:  # Want to process messages from the server first
    try:
        while True:
            gui.update()

            # Automatically sends the request to server if these are missing.
            if serverPuKey == 0:
                sendDict(prep_server_pukey_request())
            elif KDC_privkey != 0 and currentTarget is None:  # Modify switch user here...
                gui.successful_login()
                if len(gui.get_request()) != 0 and gui.get_request() != my_username:
                    currentTarget = gui.get_request()
                if currentTarget is not None:
                    if (ActiveSessionKeys.get(currentTarget) is not None):
                        gui.successful_request(currentTarget)
                    else:
                        sendDict(prep_AS_request())
            elif currentTarget is not None and gui.get_challenger() == "":
                print(0)
                currentTarget = None
                print(-1)
                gui.failed_request()
                print(-2)

            message_header = cli.recv(LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            Server_reply = json.loads(cli.recv(message_length).decode('utf-8'))

            print(Server_reply)
            if Server_reply.get('msg'):  # Display this to the user...
                print(f"From server: {Server_reply['msg']}")

            # RSA Authentication Stage
            if serverPuKey == 0 and Server_reply.get('pubkey_e'):
                serverPuKey = rsa.PublicKey(Server_reply['pubkey_n'], Server_reply['pubkey_e'])
            if KDC_privkey == 0 and Server_reply.get('KDC_prikey'):
                EncPswd = Server_reply['KDC_prikey']\
                    .to_bytes(Server_reply['EncLen'], byteorder='big')
                KDC_privkey = rsa.decrypt(EncPswd, client_privkey).decode('utf-8')

            # KDC Ticket Getting Stage
            if (Server_reply.get('Target') is None):
                # Decrypt ticket with private key, place session key in temp dict
                if(Server_reply.get('TGT')):
                    # TGT has been sent to client?
                    enc_tgt = Server_reply['TGT']
                    dec_tgt = json.loads(decrypt(enc_tgt, KDC_privkey))
                    # print(f"\nDecrypted TGT: {dec_tgt}")
                    KDC_SessionKey = dec_tgt['session_key_TGT']
                    KDC_TGS_Setup = {
                        "ID": f"{my_username}",
                        "TGS": {
                            "ID": f"{my_username}",
                            "Target": f"{currentTarget}",
                            "TGT": dec_tgt['KDC_Ticket'],
                            "auth": encrypt(str(time.time()), KDC_SessionKey)
                        }
                    }
                    sendDict(KDC_TGS_Setup)
                elif(Server_reply.get('Ticket') and currentTarget != ""):
                    if Server_reply['status'] is True:
                        ticket_dict = json.loads(decrypt(Server_reply['Ticket'], KDC_SessionKey))
                        ActiveSessionKeys[f'{currentTarget}'] = ticket_dict['session_key']
                        # print(f"Here's server Ticket replied\n{ticket_dict}")
                        if ticket_dict['target_ID'] != currentTarget:
                            print("ERROR: current target does not match the target in Ticket")
                        TicketToTarget = {
                            "ID": f"{my_username}",
                            "Target": currentTarget,
                            "Ticket": ticket_dict['TargetTicket']
                        }
                        # Sends the ticket to the target through server.
                        sendDict(TicketToTarget)
                        gui.successful_request(currentTarget)
                    else:
                        print("Ticket request failed, enter target again.")
                        # Reset the current target...
                        currentTarget = None
                        gui.failed_request()

            elif (Server_reply.get('Target')):
                # This case someone else has sent a ticket over
                # We want to decrypt it and put it in ready queue...
                if Server_reply.get('Ticket'):
                    dec_ticket = json.loads(decrypt(Server_reply['Ticket'], KDC_privkey))
                    if dec_ticket.get('requester_ID') == Server_reply['ID']:
                        ActiveSessionKeys[dec_ticket.get('requester_ID')]\
                            = dec_ticket['session_key']
                        print(f"We can chat with {Server_reply['ID']} now!")
                # This is a plain encrypted message sent from other client.
                # We want to make sure we have their session key to decrypt the message.
                # Check if the other person is in our dictionary.
                elif ActiveSessionKeys.get(Server_reply.get('ID')):
                    enc_message = Server_reply['enc_message']
                    message = decrypt(enc_message, ActiveSessionKeys[Server_reply.get('ID')])
                    gui.receive_message(Server_reply.get('ID'), message)
            if (KDC_privkey == 0 and len(gui.get_user_pass()) != 0):
                gui.failed_login()

    except IOError as e:
        # This is normal on non blocking connections
        # When there are no incoming data error is going to be raised
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        if KDC_privkey == 0 and len(gui.get_user_pass()) != 0:
            cli.send(f"{0:<{LENGTH}}".encode('utf-8'))
            my_username = gui.get_user_pass()[0]
            my_pswd = gui.get_user_pass()[1]
            username = my_username.strip().encode('utf-8')
            username_header = f"{len(username):<{LENGTH}}".encode('utf-8')

            # Reset the connection
            cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cli.connect((IP, PORT))
            cli.setblocking(False)
            
            cli.send(username_header + username)
            sendDict(prep_RSA_auth_request(my_pswd))

        if len(ActiveSessionKeys) > 0:
            # print("ActiveUsers: {", end='')
            # for key in ActiveSessionKeys:
            #     print(f" {key}", end="")
            if(gui.get_disconnected()):
                message = ""
                for key in ActiveSessionKeys:
                    sendDict({
                        'ID': my_username,
                        'Target': key,
                        'enc_message': encrypt(message, ActiveSessionKeys[currentTarget])
                    })
            else:
                message = gui.get_outbox()
                if (ActiveSessionKeys.get(currentTarget) is not None and message != ""):
                    sendDict({
                        'ID': my_username,
                        'Target': currentTarget,
                        'enc_message': encrypt(message, ActiveSessionKeys[currentTarget])
                    })
        continue

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: '.format(str(e)))
        sys.exit()
