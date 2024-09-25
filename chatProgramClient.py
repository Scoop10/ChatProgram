import json
import websockets
import asyncio
from Crypto.PublicKey import RSA
import hashlib
import base64

def sendPrivateMessage(clientKey):
    Message = input()
    
    chat = {
        "participants": [],
        "message": Message
    }

    package = {
        "type": "chat",
        "destination_server": "coming",
        "symm_key": clientKey,
        "chat": chat
    }

async def sendPublicMessage(destSocket):
    global counter
    message = input()

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
    
    await destSocket.send(serialisedRequest)
    counter = counter + 1

async def getClientList(activeSocket):
    global counter
    request = {
        "type": "client_list_request"
    }

    serialisedRequest = json.dumps(request)

    await activeSocket.send(serialisedRequest)


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
    counter = counter + 1

async def updateFingerprints():
    fingerprints.clear()
    for client in connectedClients:
        sha256_hash = hashlib.sha256(client.export_key()).digest()
        clientFingerprint = base64.b64encode(sha256_hash).decode('utf-8')
        fingerprints.append(clientFingerprint)
    
    print(fingerprints)

async def receiveMessages(websocket, stop_event):
    global counter
    global connectedServers
    while not stop_event.is_set():
        try:
            response = await websocket.recv()
            responseMessage = json.loads(response)
            print(f"Received response from server: ", responseMessage)

            if responseMessage["type"] == "client_list":
                connectedClients.clear()

                receivedServerList = responseMessage["servers"]
                connectedServers = receivedServerList

                for server in receivedServerList:
                    currentServerClients = server["clients"]
                    for clients in currentServerClients:
                        connectedClients.append(RSA.import_key(clients))

                print(connectedClients)

                await asyncio.gather(updateFingerprints())

            elif responseMessage["type"] == "client_update":
                connectedClients.clear()

                for client in responseMessage["clients"]:
                    connectedClients.append(RSA.import_key(client))
                
                print(connectedClients)

                await asyncio.gather(updateFingerprints())


            elif responseMessage["type"] == "signed_data":
                data = responseMessage["data"]
                type = data["type"]
                counter = responseMessage["counter"]

                if type == "public_chat":
                    print("Public message received from: ", data["sender"])

        except websockets.ConnectionClosed:
            print("Connection closed by server")
            stop_event.set()
            break
        except Exception as e:
            print("Exception: ", {e})
            stop_event.set()
            break

async def getUserInput(stop_event):
    loop = asyncio.get_event_loop()
    while not stop_event.is_set():
        userInput = await loop.run_in_executor(None, input, "Waiting for user input: ")
        if stop_event.is_set():
            break
        yield userInput

async def userInterface(clientSocket, stop_event):
    async for command in getUserInput(stop_event):
        if command == "Who's online?":
            await asyncio.gather(getClientList(clientSocket))
        elif command == "Send a public message":
            await asyncio.gather(sendPublicMessage(clientSocket))
        elif command == "Sign off":
            await clientSocket.close()
            break


async def main():
    stop_event = asyncio.Event()
    server = "ws://localhost:8765"
    async with websockets.connect(server) as clientSocket:
        await asyncio.gather(sendHelloMessage(clientSocket))
        receive_task = asyncio.create_task(receiveMessages(clientSocket, stop_event))
        send_task = asyncio.create_task(userInterface(clientSocket, stop_event))
        await asyncio.gather(receive_task, send_task)
        

if __name__ == "__main__":

    counter = 1

    connectedServers = []
    connectedClients = []
    fingerprints = []
    names = []

    myPrivateKey = RSA.generate(2048)
    myPublicKey = myPrivateKey.public_key()

    exportedPublicKey = myPublicKey.export_key().decode('utf-8')

    sha256_hash = hashlib.sha256(myPublicKey.export_key()).digest()

    myFingerprint = base64.b64encode(sha256_hash).decode('utf-8')

    asyncio.run(main())

    print("Ending Client Program")