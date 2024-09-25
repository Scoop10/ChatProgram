import json
import websockets
from Crypto.PublicKey import RSA
import asyncio

async def helloMessage(data, activeSocket):
    newKey = RSA.import_key(data["public_key"])
    if newKey not in client_list:
        socketList.append(activeSocket)
        client_list.append(newKey)

async def getClientList(activeSocket):
    stringClientList = []
    for keys in client_list:
        stringClientList.append(keys.export_key().decode())

    server_list[0]["clients"] = stringClientList

    request = {
        "type" : "client_list",
        "servers" : server_list,
    }
    
    serialisedClientList = json.dumps(request)

    await activeSocket.send(serialisedClientList)

    print("Sent client list")

    return

async def sendClientUpdate():
    stringClientList = []
    for keys in client_list:
        stringClientList.append(keys.export_key().decode())

    request = {
        "type" : "client_update",
        "clients" : stringClientList,
    }
    
    serialisedClientList = json.dumps(request)

    # THIS NEEDS TO BE SENT TO EACH SERVER!!!!!!!!


    for client in socketList:
        await asyncio.gather(getClientList(client))

    return

async def clientHandler(activeSocket):
    global counter
    try:
        while True:
            try:
                message = await asyncio.wait_for(activeSocket.recv(), timeout=5)
                data = json.loads(message)
                print(f"Received message: {data}")
                if data["type"] == "signed_data":
                    if counter >= data["counter"]:
                        print("Counter exception!")
                        

                    # WIll need to insert decryption code here!!



                    receivedData = data["data"]

                    if receivedData["type"] == "hello":
                        await asyncio.gather(helloMessage(receivedData, activeSocket))
                        print("Hello message Received")
                        await asyncio.gather(sendClientUpdate())
                        counter = data["counter"]
                        continue
                    elif receivedData["type"] == "public_chat":
                        print("Received public chat message")
                        await asyncio.gather(receivePublicMessage(receivedData))
                        counter = data["counter"]
                        continue
                elif data["type"] == "client_list_request":
                    await asyncio.gather(getClientList(activeSocket))
                    continue
            except asyncio.TimeoutError:
                await activeSocket.ping()

    except websockets.ConnectionClosed:
        index = socketList.index(activeSocket)
        print(client_list[index], " Disconnected. Connection Closed!")
    finally:
        index = socketList.index(activeSocket)
        socketList.remove(activeSocket)
        client_list.remove(client_list[index])
        await asyncio.gather(sendClientUpdate())

async def receivePublicMessage(data):
    serialisedData = json.dumps(data)
    await asyncio.gather(sendPublicMessage(serialisedData))

async def sendPublicMessage(data):
    for client in socketList:
        await client.send(data)

async def startServer():
    server = await websockets.serve(clientHandler, host, port)
    await server.wait_closed()


# connection code

if __name__ == '__main__':
    port = 8765
    # host = "192.168.20.49" # Laptop
    host = "localhost" # PC

    counter = 0

    print("Starting Server on IP: ", host, " and port: ", port)
    socketList = []
    client_list = []
    server_list = []

    # Append this server to the server_list

    server_list.append({"address" : host, "clients" : client_list})

    asyncio.run(startServer())