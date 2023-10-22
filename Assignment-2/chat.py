import socket
import threading

# Global variables 
exit_flag = False       # flag to exit threads
connected = False
address = None
host_ip = None

# Get the hostname and IP address of the server
hostname = socket.gethostname()
server_address = socket.gethostbyname(hostname)


def print_commands():
    """Prints a list of available commands based on the connection status."""
    global connected
    if connected == False:
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


def start_socket(server_port):
    """Creates and configures a socket to listen for connections."""
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


def connect(serverIP, serverPort):
    """Attempts to connect to a chat server."""
    global connected, chat_connection
    # create a client socket 
    try:
        chat_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as errorMessage:
        print(f"\nFailed to create client socket. Error: {errorMessage}")
        return
    # connect to the server
    try:
        chat_connection.connect((serverIP, serverPort))
        print(f"\nSuccessfully connected with {serverIP}\n")
        connected = True
    except socket.error as errorMessage:
        print(f"\nFailed to connect to client. Error: {errorMessage}")
        chat_connection.close()
        return


def disconnect():
    """Disconnects from the chat server."""
    global connected, chat_connection, address, host_ip
    connected = False
    if address == None:
        print(f"\nDisconnected from {host_ip}\n")
    else:
        print(f"Disconnected from {address}\n")
    chat_connection.close()


def send(message):
    """Sends a message to the connected chat server."""
    global connected, chat_connection
    if connected == True:
        if chat_connection != None:
            chat_connection.send(message.encode())
            print(f"Message \"{message}\" sent")
    else:
        print("\nNot connected to a chat. Please connect to a chat before sending a message.")


def receive_message():
    """Receives messages from the chat server."""
    global connected, chat_connection, host_ip, exit_flag, address
    while not exit_flag:
        try:
            if connected == True:
                message = chat_connection.recv(1024).decode()
                if not message:
                    # If the received message is empty, it's a sign of disconnection.
                    if address != None:
                        print(f"\n\nHost at {address} disconnected\n\nEnter command: ", end="")
                        address = None
                    else:
                        print(f"\n\nHost at {host_ip} disconnected\n\nEnter command: ", end="")
                        host_ip = None
                    chat_connection.close()
                    connected = False
                elif message:
                    print(f"\nMessage \"{message}\" received \n\nEnter command: ", end="")
            else:
                pass
        except (ConnectionResetError, ConnectionAbortedError) as errorMessage:
            if address != None:
                print(f"\n\nHost at {address} disconnected\n\nEnter command: ", end="")
            chat_connection.close()
            connected = False
        except socket.error as errorMessage:
            chat_connection.close()
            connected = False


def wait_for_connection(server_port):
    """Waits for incoming chat connections."""
    global connected, chat_connection, client_address, server_socket, address
    server_socket = start_socket(server_port)
    while not exit_flag: 
        if connected == False:
            try:
                chat_connection, client_address = server_socket.accept()
                address = client_address[0]
                print(f"\n\nAccepted connection with {address}\n\nEnter command: ", end="")
                connected = True
            except socket.error as errorMessage:
                pass
        else:
            pass


def main():
    global exit_flag, connected, server_socket, chat_connection, server_port, host_ip
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

    # start thread to listen for incoming connections
    server_thread = threading.Thread(target=wait_for_connection, args=(server_port,))
    server_thread.start()

    # start thread to receive messages
    receive_thread = threading.Thread(target=receive_message)
    receive_thread.start()

    print(f"\nChat running at {server_address} on port {server_port}")
    # print initial command list
    print_commands()

    # loop to handle main program commands 
    while True:
        try:
            command = input("Enter command: ")
        except ValueError:
            print("Invalid input. Please enter a valid command from the list. \nType 'help' to see the list of commands.\n")
        # split command into parts
        commandParts = command.split()
        # check if command is valid when nothing is input
        if len(commandParts) < 1:
            print("Invalid command. Please enter a valid command from the list. \nType 'help' to see the list of commands.\n")
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
                        host_port = int(commandParts[2])
                        if host_port < 10000 or host_port > 20000:
                            print("Port number must be between 10,000 and 20,000.")
                        else:
                            host_ip = commandParts[1]
                            connect(host_ip, host_port)
                else: 
                    print("Already connected to a chat. Please disconnect before connecting to another chat.")
            elif commandParts[0] == "send":
                if connected == True:
                    # check if message is attached to command "send"
                    if len(commandParts) < 2:
                        print("Command message was received, but no message was attached to command.")
                        print("Expected format: send <message>")
                    else:
                        # craft message to be sent, remove command "send" from messages
                        message = ' '.join(commandParts[1:])
                        # call function to send message 
                        send(message)
                else:
                    print("Not connected to a chat. Please connect to a chat before sending a message.\n")
            # handle disconnect command
            elif commandParts[0] == "disconnect":
                if connected == True:
                    disconnect()
                else:
                    print("Not connected to a chat. Disconnect command is not available.\n")
            # handle exit command
            elif commandParts[0] == "exit":
                exit_flag = True        # set exit flag to true to exit threads
                server_socket.close()   # close server socket
                chat_connection.close() # close chat connection socket
                server_thread.join()    # wait for server thread to finish
                receive_thread.join()   # wait for receive thread to finish
                exit(0)                 # exit program gracefully
            # handle invalid command
            else:
                print("Invalid command. Please enter a valid command from the list.\nType 'help' to see the list of commands.\n")


if __name__ == "__main__":
    main()