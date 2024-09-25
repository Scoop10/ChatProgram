import json
import websockets
from Crypto.PublicKey import RSA
import asyncio

# This function is called when a hello message is received from a client
# It checks if the client who sent the hello is in the currently connected clients list.
# If not it adds the clients socket to the socket list and the clients public key to the connected clients list
# data is the data which has been extracted from the hello message and activeSocket is the socket which the client is currently connected on
async def helloMessage(data, activeSocket):
    # Create a new RSA key object from the public_key string which is sent in the data package
    newKey = RSA.import_key(data["public_key"])
    # If the key is not in the current connected client_list
    if newKey not in client_list:
        # Append the current client socket (activeSocket) to the servers socketList (which keeps track of all open sockets)
        socketList.append(activeSocket)
        # Append the new RSA key object to the currently connected client_list (This is at the same index as the socket which the client is connected on so that they are effectively linked)
        client_list.append(newKey)

# This function is called when the server receives a client_list_request message.
# The function sends a client_list message back to the socket which requested it
# activeSocket is the socket which the client who requested the list is connected on
async def getClientList(activeSocket):

# THIS CODE SHOULD POSSIBLY BE MOVED TO THE HELLO MESSAGE FUNCTION

    # Initialise an empty list to store the RSA public key strings in
    stringClientList = []
    # Iterate through all the currently connected clients
    for keys in client_list:
        # For each currently connected client export the equivalent RSA key string and append that string to the stringClientList
        stringClientList.append(keys.export_key().decode())

    # Update the server_list with the currently connected clients
    server_list[0]["clients"] = stringClientList

# END OF CODE TO POSSIBLE BE MOVED

    # Request needs to have the below format as per the specification
    # server_list is the above list of exported RSA public keys
    request = {
        "type" : "client_list",
        "servers" : server_list,
    }
    
    # Serialise the request into a JSON formatted string
    serialisedClientList = json.dumps(request)
    # Send the serialisedClientList over the socket corresponding to the client who requested the client_list
    await activeSocket.send(serialisedClientList)

    # SERVER SIDE CONFIRMATION - NOT NECESSARY
    print("Sent client list")

    return


# This function is called when a server requests a client_update because a client has either said hello or disconnected
# The function compiled a client_update message and sends it to all servers (THIS HAS NOT YET BEEN IMPLEMENTED!!!!!)
async def sendClientUpdate():
    # Initialise an empty list to store the RSA public key strings in
    stringClientList = []
    # Iterate through all the currently connected clients
    for keys in client_list:
        stringClientList.append(keys.export_key().decode())
    # Request needs to have the below format as per the specification
    # server_list is the above list of exported RSA public keys
    request = {
        "type" : "client_update",
        "clients" : stringClientList,
    }
    # Serialise the request into a JSON formatted string
    serialisedClientList = json.dumps(request)

    ## THIS NEEDS TO BE SENT TO EACH SERVER!!!!!!!! ##

# This function is called when either a public or a private chat is received from a client on this server
# The function sends the message to every server
# Data is a serialised JSON String package which is to be sent to all servers
## THIS NEEDS TO BE COMPLETED ##
async def sendToAllServers(data):
    ## UNCOMMENT AND FINISH THIS CODE WHEN THE SERVER CONNECTIONS HAVE BEEN DEALT WITH ##

    # Iterate through all servers
    # for server in serverSocketList:
        # Send the public_chat to all servers
    #     await server.send(serialisedData)
    return

# This function is the main handler of all clients. Each client has an individual socket
# The general purpose of this function is to receive messages from clients and to call or perform the correct functions based on the type of message received
# activeSocket is the current socket which the client in this async process is running on
async def clientHandler(activeSocket):
    # COUNTER NEEDS TO BE DEALT WITH THIS WILL BE REMOVED
    global counter
    # Try is used so that if an exception occurs it is handled properly
    try:
        # This loop should run until an exception is encountered (such as the socket closing)
        while True:
            try:
                # Wait for a message to be received on the server socket. Timeout = 5 is to detect when the client drops off. 
                # (Every 5 seconds a ping will be sent to test if the client is still online)
                message = await asyncio.wait_for(activeSocket.recv(), timeout=5)
                # When a message is received deserialised the received JSON object
                data = json.loads(message)
                # SERVER SIDE CONFIRMATION
                print(f"Received message: {data}")
                # If the data received is a signed_data package
                if data["type"] == "signed_data":                 
                    # Get the actual data segment of the received package
                    receivedData = data["data"]
                    # If a hello messahe has been received
                    if receivedData["type"] == "hello":
                        # Call the helloMessage function as a coroutine to execute concurrently
                        await asyncio.gather(helloMessage(receivedData, activeSocket))
                        # SERVER SIDE CONFIRMATION
                        print("Hello message Received")
                        ## THIS WILL BE REMOVED AS I NEED TO WORK ON THIS ##
                        counter = data["counter"]
                        # Go back to the start of the loop and wait for the next message
                        continue
                    # If a public_chat type of message has been received
                    elif receivedData["type"] == "public_chat":
                        # SERVER SIDE CONFIRMATION
                        print("Received public chat message")
                        # Convert the public_chat into a serialised JSON String
                        serialisedData = json.dumps(data)
                        # Schedule the data to be broadcast to all servers
                        await asyncio.gather(sendToAllServers(serialisedData))
                        ## THIS WILL BE REMOVED AS I NEED TO WORK ON THIS ##
                        counter = data["counter"]
                        # Go back to the start of the loop and wait for the next message
                        continue
                # Else if the received message is a client_list_request
                elif data["type"] == "client_list_request":
                    # Call the getClientList function in a coroutine with the activeSocket as the arg
                    await asyncio.gather(getClientList(activeSocket))
                    # Go back to the start of the loop and wait for the next message
                    continue
            # If the socket doesn't receive a message for 5 seconds
            except asyncio.TimeoutError:
                # Send a ping to check if the socket is still online
                await activeSocket.ping()
    # If an exception occurs as the client disconnected
    except websockets.ConnectionClosed:
        # Find the socket which disconnected
        index = socketList.index(activeSocket)
        # SERVER SIDE CONFIRMATION
        print(client_list[index], " Disconnected. Connection Closed!")
    finally:
        # Remove the disconnected socket from the socketList
        socketList.remove(activeSocket)
        # Remove the disconnected client  from the connected clients
        client_list.remove(client_list[index])
        # Send a client update to all servers as a client disconnected
        await asyncio.gather(sendClientUpdate())

# This function is used to start the server
async def startServer():
    # Start the server on the host and port specified. "URL" will be ws://host:port
    server = await websockets.serve(clientHandler, host, port)
    # Wait until the server is closed then return
    await server.wait_closed()


# Main
if __name__ == '__main__':
    # Specify the port
    port = 8765
    # Specify the host
    host = "localhost" # PC
    ## THIS WILL BE REMOVED ONCE COUNTER STUFF IS FIGURED OUT ## 
    counter = 0
    # SERVER SIDE CONFIRMATION
    print("Starting Server on IP: ", host, " and port: ", port)
    # Initialise empty lists for the required info to be stored:
    # socketList stores active sockets, client_list stores active clients RSA keys
    socketList = []
    client_list = []
    
    # server_list will have all of the neighborhood servers manually entered
    server_list = []

    # Append this server to the server_list
    server_list.append({"address" : host, "clients" : client_list})
    # Start the server
    asyncio.run(startServer())