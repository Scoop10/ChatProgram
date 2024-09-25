import json
import socket
from Crypto.PublicKey import RSA
import hashlib
import time

def sendPrivateMessage(clientKey, destServer):
    Message = input()
    
    chat = {
        "participants": [],
        "message": Message
    }

    package = {
        "type": "chat",
        "destination_server": destServer,
        "symm_key": clientKey,
        "chat": chat
    }

def sendPublicMessage(myKey, message):

    data = {
        "type": "public_chat",
        "public_key": myKey,
        "message": message
    }

def getClientList(destSocket):
    request = {
        "type": "client_list"
    }

    serialisedRequest = json.dumps(request).encode('utf-8')

    destSocket.send(serialisedRequest)

    data = destSocket.recv(4096)

    receivedClientList = json.loads(data)

    print(receivedClientList)

    return





def sendHelloMessage(destSocket, key):
    request = {
        "type" : "hello",
        "public_key" : key
    }

    serialisedRequest = json.dumps(request).encode('utf-8')

    destSocket.send(serialisedRequest)

    return




myKey = RSA.generate(2048)

# myFingerprint = hashlib.sha256(myKey)

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = 80

# host = "192.168.20.49" # Laptop
host = "192.168.20.24" # PC

exportedKey = myKey.export_key().decode()

clientSocket.connect((host, port))

sendHelloMessage(clientSocket, exportedKey)

getClientList(clientSocket)

closeRequest = {"type" : "CLOSE"}

time.sleep(5)

clientSocket.send(json.dumps(closeRequest).encode('utf-8'))

print("Ending Client Program")

# {
#     type: "data_container",
#     data: { ... },
#     counter: <64-bit integer counter>, need to check this against the last sent message
#     signature: "<Base64 signed hash of data concatenated with counter>" (SHA256 algorithm)
# }