import socket 

# Get the hostname and IP address of the server
hostname = socket.gethostname()
serverAddress = socket.gethostbyname(hostname)

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

# create a socket  
try:
    chatSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as errorMessage:
    print(f"Failed to create client socket. Error: {errorMessage}")
    exit(1)

# inform user that chat is ready to start
print(f"Chat running at {serverAddress} on port {serverPort}\n")

# variable to keep track of whether we are connected to a chat
connected = False

# can add if to see if we need to print commands inside while loop
def print_commands():
    if connected == False:
        # print command list 
        print("List of commands:") 
        print("connect <IP address> <port number>")
        print("help")
        print("exit\n")
    elif connected == True:
        print("List of commands:") 
        print("send <message>")
        print("disconnect")
        print("help")
        print("exit\n")

# function to connect to server
def connect(serverIP, serverPort):
    print("connect command")
        # connect to the server
    try:
        chatSocket.connect((serverIP, serverPort))
    except socket.error as errorMessage:
        print(f"Failed to connect to client. Error: {errorMessage}")
        # chatSocket.close()
        exit(1)

# function to disconnect from server
def disconnect():
    print("disconnect command")
    connected == False

# print initial command list
print_commands()


# loop while we are not connected to a chat or until user exits
while  connected == False:
    try:
        command = input("Enter command: ")
    except ValueError:
        print("Invalid input. Please enter a valid command from the list.")
        print("Type 'help' to see the list of commands.\n")
    # split command into parts
    commandParts = command.split()
    # check if command is valid when nothing is input
    if len(commandParts) < 1:
        print("Invalid command. Please enter a valid command from the list.")
    # command is not empty so check if it is valid
    else:
        # handle command help
        if commandParts[0] == "help":
            print_commands()
        # handle connect command
        elif commandParts[0] == "connect":
            # check if arguments are valid 
            if len(commandParts) != 3:
                print("Expected format: connect <IP address> <port number>")
            else:
                # check if port number is valid
                serverPort = int(commandParts[2])
                if serverPort < 10000 or serverPort > 20000:
                    print("Port number must be between 10,000 and 20,000.")
                else:
                    connect(commandParts[1], serverPort)
        # handle exit command
        elif commandParts[0] == "exit":
            print("exit command")
            break
        # handle invalid command
        else:
            print("Invalid command. Please enter a valid command from the list.")

# loop while we are connected 
while connected == True:
    try:
        command = input("Enter command: ")
    except ValueError:
        print("Invalid input. Please enter a valid command from the list.")
        print("Type 'help' to see the list of commands.\n")
    # split command into parts
    commandParts = command.split()
    # check if command is valid when nothing is input
    if len(commandParts) < 1:
        print("Invalid command. Please enter a valid command from the list.")
    # command is not empty so check if it is valid
    else:
        # handle command help
        if commandParts[0] == "help":
            print_commands()
        # handle send command        
        elif commandParts[0] == "send":
            print("send command")
        # handle disconnect command
        elif commandParts[0] == "disconnect":
            print("disconnect command")
            # disconnect()
        # handle exit command
        elif commandParts[0] == "exit":
            print("exit command")
            break
        # handle invalid command
        else:
            print("Invalid command. Please enter a valid command from the list.")
    
    # testing 
    # print(commandParts)
    # print(len(commandParts))
    # print(commandParts[0])
