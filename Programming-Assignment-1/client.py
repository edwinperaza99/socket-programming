import socket 

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

# ask for IP address to connect to
serverIP = input("Enter server IP address: ")

# create a client socket 
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the server
try:
    clientSocket.connect((serverIP, serverPort))
except socket.error as errorMessage:
    print(f"Failed to connect to client. Error: {errorMessage}")
    clientSocket.close()
    exit(1)

print("\nClient has connected to the server!\n")

while True:
    message = input("Enter a message to send to server: ")
    print("Client sending message:", message)
    if message == "quit":
        clientSocket.send(message.encode())
        print("Client informing server that it is quitting.")
        try:
            messages = clientSocket.recv(2048).decode()
            if not messages:
                print("No messages were received from server messages log.")
                break
            print("Client received messages log")
            print(messages)
            break
        except socket.error as errorMessage:
            print(f"Failure in receiving messages log. Error: {errorMessage}")
            clientSocket.close()
            exit(1)
    else:
        clientSocket.send(message.encode())

clientSocket.close()

# message that program has finished
print("\nClient has closed the connection to the server.\n")