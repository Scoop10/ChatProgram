import json
import websockets
import asyncio
from Crypto.PublicKey import RSA
import hashlib
import time
import base64

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

def sendPublicMessage(destSocket, message):

    request = {
        "type":"signed_data",
        "data": {
                "type": "public_chat",
                "sender": myFingerprint,
                "message": message
            },
        "counter": counter,
        "signature":"coming"
    }

    serialisedRequest = json.dumps(request)
    
    destSocket.send(serialisedRequest.encode('utf-8'))



async def getClientList(activeSocket):
    global counter
    request = {
        "type": "client_list_request"
    }

    serialisedRequest = json.dumps(request)

    await activeSocket.send(serialisedRequest)

    message = await activeSocket.recv()

    receivedClientMessage = json.loads(message)

    connectedClients.clear()

    receivedServerList = receivedClientMessage["servers"]

    for server in receivedServerList:
        currentServerClients = server["clients"]
        for clients in currentServerClients:
            connectedClients.append(RSA.import_key(clients))

    print(connectedClients)

    return


async def sendHelloMessage(activeSocket):
    global counter

    request = {
        "type":"signed_data",
        "data": {
            "type" : "hello",
            "public_key" : exportedPublicKey
        },
        "counter": counter,
        "signature":"coming"
    }

    serialisedRequest = json.dumps(request)

    await activeSocket.send(serialisedRequest)


async def main():
    server = "ws://localhost:8765"  # List of server URIs
    async with websockets.connect(server) as clientSocket:
        await asyncio.gather(sendHelloMessage(clientSocket))
        time.sleep(2)
        await asyncio.gather(getClientList(clientSocket))
        time.sleep(20)
        await clientSocket.close()

    

if __name__ == "__main__":

    counter = 0

    connectedClients = []

    myPrivateKey = RSA.generate(1024)
    myPublicKey = myPrivateKey.public_key()

    # myFingerprint = hashlib.sha256(myKey)

    port = 80

    # host = "192.168.20.49" # Laptop
    host = "192.168.20.24" # PC

    exportedPublicKey = myPublicKey.export_key().decode('utf-8')

    sha256_hash = hashlib.sha256(myPublicKey.export_key()).digest()

    myFingerprint = base64.b64encode(sha256_hash).decode('utf-8')

    print(myFingerprint)

    asyncio.run(main())

    # clientSocket.connect((host, port))

    # sendHelloMessage(clientSocket)

    # time.sleep(2)

    # getClientList(clientSocket)

    # time.sleep(2)

    # publicMessage = input()

    # sendPublicMessage(clientSocket, publicMessage)

    print("Ending Client Program")