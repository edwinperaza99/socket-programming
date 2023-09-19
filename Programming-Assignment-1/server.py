import socket

# array to store messages from client 
messages = []

# receive server port from user 
serverPort = int(input("Enter server port: "))

# create a server socket 
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the port number to the server socket 
serverSocket.bind(('', serverPort))

# Get the hostname and IP address of the server
hostname = socket.gethostname()
serverAddress = socket.gethostbyname(hostname)

# Print server details
print("Server hostname is:", hostname)
print("Server is at address:", serverAddress)
print("Server is using port:", serverPort)

# wait for a connection to the server 
serverSocket.listen(1)

# accept the connection from the client 
connection, clientAddress = serverSocket.accept()
print("Server connected to client at address:", clientAddress)

while True:
    message = connection.recv(2048).decode()
    # check if the message is quit, if not just continue with loop
    if message == "quit":
        print("The client has informed the server that it is quitting.")
        for message in messages:
            connection.send(message.encode())
        break
    else:
        print("Server received message:", message)
        messages.append(message)

# close the connection between client and server
connection.close()