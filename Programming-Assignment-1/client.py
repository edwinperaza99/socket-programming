import socket 

# ask for IP address and port number from user
serverPort = int(input("Enter server port number: "))
serverIP = input("Enter server IP address: ")

# create a client socket 
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clientSocket.connect((serverIP, serverPort))
print("Client has connected to the server!")

while True:
    message = input("Enter a message to send to server: ")
    print("Client sending message:", message)
    if message == "quit":
        clientSocket.send(message.encode())
        print("Client informing server that it is quitting.")
        messages = clientSocket.recv(2048).decode()
        print("Client received messages log")
        print(messages)
        break
    else:
        clientSocket.send(message.encode())

clientSocket.close()