from Library.KDC import *

KDC_Server = KDC()

tempRequest = {
    "ID" : "Alice",
    "Password" : "AlicePass",
    "Target" : "Bob"
}

print(KDC_Server.TicketGeneration(tempRequest))