import socket
import threading
import time

# Get the hostname and IP address of the server
hostname = socket.gethostname()
server_address = socket.gethostbyname(hostname)

# define exit flag for threads 
exit_flag = False

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

def start_server(server_port):
    # create a socket
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
    return server_socket

# function to connect to server
def connect(serverIP, serverPort):
    global connected, chat_connection
    # create a client socket 
    try:
        chat_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as errorMessage:
        print(f"Failed to create client socket. Error: {errorMessage}")
        return
    # connect to the server
    try:
        chat_connection.connect((serverIP, serverPort))
        print(f"\nChat connected at {serverIP} on port {serverPort}\n")
        connected = True
    except socket.error as errorMessage:
        print(f"Failed to connect to client. Error: {errorMessage}")
        chat_connection.close()
        return

# function to disconnect from server
def disconnect():
    global connected, chat_connection, server_port
    print("\nDisconnecting...")
    message = "DISCONNECT NOW"
    chat_connection.send(message.encode())
    chat_connection.close()
    server_socket.close()
    start_server(server_port)
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
    while not exit_flag:
        try:
            if connected == True:
                message = chat_connection.recv(1024).decode()
                if message == "DISCONNECT NOW":
                    disconnect()
                elif message:
                    print(f"\nMessage received: {message}\nEnter command: ", end="")
            else:
                pass
        except socket.error as errorMessage:
            print(f"Failure in message reception. Error: {errorMessage}")
            # chat_connection.close()
            # exit(1)

def wait_for_connection(server_port):
    global connected, chat_connection, client_address, server_socket
    server_socket = start_server(server_port)
    # # create a socket
    # try:
    #     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # except socket.error as errorMessage:
    #     print(f"Failed to create client socket. Error: {errorMessage}")
    #     exit(1)
    # try:
    #     server_socket.bind(('', server_port))
    # except socket.error as errorMessage:
    #     print(f"Failed to bind socket. Error: {errorMessage}")
    #     exit(1)
    # server_socket.listen(1)

    # loop to check for connection
    while not exit_flag: 
        if connected == False:
            try:
                chat_connection, client_address = server_socket.accept()
                print(f"\n\nChat connected to address: {client_address[0]}\nEnter command: ", end="")
                connected = True
                
            except socket.error as errorMessage:
                pass
        else:
            pass

def main():
    global exit_flag, connected, server_socket, chat_connection, server_port
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
                            print (f"\nConnecting to {commandParts[1]} on port {commandParts[2]}")
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
                    disconnect()
                else:
                    print("Not connected to a chat. Disconnect command is not available.")
            # handle exit command
            elif commandParts[0] == "exit":
                print("\nExiting program in:")
                exit_flag = True
                server_socket.close()
                chat_connection.close()
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