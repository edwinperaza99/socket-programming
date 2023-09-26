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

# inform user that chat is ready to start
print(f"Chat running at {serverAddress} on port {serverPort}\n")

# print command list 
print("List of commands:") 
print("connect <IP address> <port number>")
print("send <message>")
print("disconnect")
print("exit\n")

while True:
    try:
        command = input("Enter command: ")
    except ValueError:
        print("Invalid input. Please enter a valid command from the list.")

    # split command into parts
    commandParts = command.split()

    # check if command is valid when nothing is input
    if len(commandParts) < 1:
        print("Invalid command. Please enter a valid command from the list.")

    else:
        # handle command connect 
        if commandParts[0] == "connect":
            print("connect command")

        # handle send command        
        elif commandParts[0] == "send":
            print("send command")
        
        # handle disconnect command
        elif commandParts[0] == "disconnect":
            print("disconnect command")
        
        # handle exit command
        elif commandParts[0] == "exit":
            print("exit command")
            break

        # handle invalid command
        else:
            print("Invalid command. Please enter a valid command from the list.")
    

    print(commandParts)
    print(len(commandParts))
    # print(commandParts[0])



# create a socket 
# try:
#     chatSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# except socket.error as errorMessage:
#     print(f"Failed to create chat socket. Error: {errorMessage}")
#     exit(1)