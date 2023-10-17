import socket
import threading
import time

# Get the hostname and IP address of the server
hostname = socket.gethostname()
server_address = socket.gethostbyname(hostname)

# define exit flag for threads 
exit_flag = threading.Event()

# variable to keep track of whether we are connected to a chat
connected = False

# store the socket of the client 
# chat_connection = None

# can add if to see if we need to print commands inside while loop
def print_commands():
    """ 
    Prints the list of commands that the user can enter.
    
    It prints different commands depending if the user is connected or waiting for a connection
    """
    global connected
    if connected == False:
        # print command list 
        print("\nList of commands:") 
        print("connect <IP address> <port number>")
        print("help")
        print("exit\n")
    elif connected == True:
        print("\nList of commands:") 
        print("send <message>")
        print("disconnect")
        print("help")
        print("exit\n")

# function to connect to server
def connect(serverIP, serverPort):
    global connected, chat_connection
    print("connect command")
    # create a client socket 
    try:
        chat_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as errorMessage:
        print(f"Failed to create client socket. Error: {errorMessage}")
        return
    # connect to the server
    try:
        chat_connection.connect((serverIP, serverPort))
    except socket.error as errorMessage:
        print(f"Failed to connect to client. Error: {errorMessage}")
        chat_connection.close()
        return
    print(f"\nChat connected at {serverIP} on port {serverPort}\n")
    connected = True

# function to disconnect from server
def disconnect():
    global connected, chat_connection
    print("disconnect command")
    if chat_connection != None:
        chat_connection.close()
        # chat_connection = None
    print("Chat disconnected.")
    connected = False

# function to send message 
def send(message):
    global connected, chat_connection
    if connected == True:
        if chat_connection != None:
            chat_connection.send(message.encode())
            print(f"Message \"{message}\" sent")
    # we do not have a connection 
    else:
        print("Not connected to a chat. Please connect to a chat before sending a message.")

    # testing 
    # print(commandParts)
    # print(len(commandParts))
    # print(commandParts[0])

def receive_message():
    global connected, chat_connection
    while not exit_flag.is_set:
        try:
            if connected == True:
                message = chat_connection.recv(1024).decode()
                if message:
                    print(f"Message received: {message}")
            else:
                pass
        except socket.error as errorMessage:
            print(f"Failure in message reception. Error: {errorMessage}")
            # chat_connection.close()
            # exit(1)

def wait_for_connection(server_port):
    global connected, chat_connection, client_address, server_socket
    # create a socket
    print("Waiting for connection...")
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as errorMessage:
        print(f"Failed to create client socket. Error: {errorMessage}")
        exit(1)
    try:
        server_socket.bind(('', server_port))
    except socket.error as errorMessage:
        print(f"Failed to bind socket. Error: {errorMessage}")
        exit(1)
    server_socket.listen(1)
    client_connection, client_address = server_socket.accept()
    print_commands()
    # loop to check for connection
    while not exit_flag.is_set: 
        print("Waiting for connection... inside loop")
        if connected == False:
            try:
                client_connection, client_address = server_socket.accept()
                print("Server connected to client at address:", client_address, end="\n\n")
                connected = True

                # print new commands 
                print_commands()
                
            except socket.error as errorMessage:
                pass
        else:
            pass

def main():
    global exit_flag, connected, server_socket
    # ask for port number to connect to and check that it is in the range of 10,000 to 20,000
    while True:
        try:
            server_port = int(input("Enter server port number: "))
            if server_port >= 10000 and server_port <= 20000:
                break
            else:
                print("Port number must be between 10,000 and 20,000.")
        except ValueError:
            print("Invalid input. Port number must be an integer.")

    # listen for incoming connections
    server_thread = threading.Thread(target=wait_for_connection, args=(server_port,))
    server_thread.start()

    receive_thread = threading.Thread(target=receive_message)
    receive_thread.start()

    # inform user that chat is ready to start
    print(f"\nChat running at {server_address} on port {server_port}")
    
    # print initial command list
    print_commands()

    # loop to handle main program commands 
    while True:
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
            elif commandParts[0] == "connect":
                # check if we are not already connected
                if connected == False:
                    # check if arguments are valid 
                    if len(commandParts) != 3:
                        print("Expected format: connect <IP address> <port number>")
                    else:
                        # check if port number is valid
                        serverPort = int(commandParts[2])
                        if serverPort < 10000 or serverPort > 20000:
                            print("Port number must be between 10,000 and 20,000.")
                        else:
                            print (f"Connecting to {commandParts[1]} on port {commandParts[2]}")
                            connect(commandParts[1], serverPort)
                else: 
                    print("Already connected to a chat. Please disconnect before connecting to another chat.")
            elif commandParts[0] == "send":
                if connected == True:
                    if len(commandParts) < 2:
                        print("Command message was received, but no message was attached to command.")
                        print("Expected format: send <message>")
                    else:
                        # craft message to be sent, remove command "send" from message
                        message = ' '.join(commandParts[1:])
                        # call function to send message 
                        send(message)
                else:
                    print("Not connected to a chat. Please connect to a chat before sending a message.")
            # handle disconnect command
            elif commandParts[0] == "disconnect":
                if connected == True:
                    print("disconnect command")
                else:
                    print("Not connected to a chat. Disconnect command is not available.")
            # handle exit command
            elif commandParts[0] == "exit":
                print("\nExiting program in:")
                server_socket.close()
                exit_flag.set()
                server_thread.join()
                receive_thread.join()
                for i in range(3, 0, -1):
                    print(i)
                    time.sleep(1)  # Sleep for 1 second
                print("\nExited program.\n")
                exit(0)
            # handle invalid command
            else:
                print("Invalid command. Please enter a valid command from the list.")



if __name__ == "__main__":
    main()