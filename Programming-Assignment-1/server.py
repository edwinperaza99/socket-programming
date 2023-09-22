import socket

# array to store messages from client 
messages = []

# ask for port number to connect to and check that it is in the range of 10,000 to 20,000
while True:
    try:
        serverPort = int(input("Enter server port number: "))
        if serverPort >= 10000 and serverPort <= 20000:
            break
        else:
            print("Port number must be between 10,000 and 20,000.")
    except ValueError:
        print("Invalid input. Port number must be an integer.")

# create a server socket 
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the port number to the server socket 
try:
    serverSocket.bind(('', serverPort))
except socket.error as errorMessage:
    print(f"Failed to bind port number. Error: {errorMessage}")
    exit(1)

# Get the hostname and IP address of the server
hostname = socket.gethostname()
serverAddress = socket.gethostbyname(hostname)

# Print server details
print("Server hostname is:", hostname)
print("Server is at address:", serverAddress)
print("Server is using port:", serverPort, end="\n\n")

# wait for a connection to the server 
try:
    serverSocket.listen(1)
except socket.error as errorMessage:
    print(f"Failure while waiting for connection. Error: {errorMessage}")
    serverSocket.close()
    exit(1)

# accept the connection from the client 
try:
    connection, clientAddress = serverSocket.accept()
except socket.error as errorMessage:
    print(f"Failure in accepting connection. Error: {errorMessage}")
    serverSocket.close()
    exit(1)


print("Server connected to client at address:", clientAddress, end="\n\n")

while True:
    try:
        message = connection.recv(2048).decode()
        # check if the message is quit, if not just continue with loop
        if message == "quit":
            print("\nThe client has informed the server that it is quitting.")
            # with join we separate the messages with a new line and we send messages to client
            connection.send("\n".join(messages).encode())
            break
        else:
            print("Server received message:", message)
            # store message in log 
            messages.append(message)
    except socket.error as errorMessage:
        print(f"Failure in message reception. Error: {errorMessage}")
        serverSocket.close()
        exit(1)

# close the connection between client and server
connection.close()
serverSocket.close()

# message that program has finished
print("\nServer has closed the connection with the client.\n")