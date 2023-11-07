import threading
import socket

# Global variables
exit_flag = False
connected = False
SOCKETS_LIST = []

# Get the hostname and IP address of the server
hostname = socket.gethostname()
server_address = socket.gethostbyname(hostname)


# TODO: I think this is done
def print_commands():
    """Prints a list of available commands based on the connection status."""
    global connected
    print("\nList of commands:") 
    print("connect <IP address> <port number>")
    if connected == True:
        print("send <host-IP or alias> <message>")
        print("disconnect <host-IP or alias>")
    print("help")
    print("exit\n")


# TODO: I think this is done
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
    global connected, SOCKETS_LIST
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
        # Prompt the user for an alias
        while True:
            response = input("Do you want to set an alias? (y/n): ").strip().lower()
            if response == "y" or response == "yes":
                alias = input("Enter an alias: ")
            elif response == "n" or response == "no":
                alias = serverIP
            else:
                print(f"Invalid response. Please send yes(y) or no(n).")
                # TODO: might need to try with "pass"
                continue
            # Check if the alias already exists in SOCKETS_LIST
            alias_exists = any(socket['alias'] == alias for socket in SOCKETS_LIST)
            if not alias_exists:
                break  # Exit the loop if the alias is unique
            print(f"Alias '{alias}' is already in use. Please choose a different alias.")
        SOCKETS_LIST.append({'socket': chat_connection, 'address': (serverIP, serverPort), 'alias': alias})
        if connected == False:
            connected = True
    except socket.error as errorMessage:
        print(f"\nFailed to connect to the client. Error: {errorMessage}")
        chat_connection.close()
        return
    

def disconnect(alias):
    """Disconnects from the chat server."""
    global connected, SOCKETS_LIST
    alias_found = False
    for socket in SOCKETS_LIST:
        if socket['alias'] == alias:
            print(f"Disconnected from {socket['alias']}\n")
            socket['socket'].close()
            SOCKETS_LIST.remove(socket)
            alias_found = True
            break
    if alias_found == False:
        print(f"Alias '{alias}' not found. Please try again.")
    if len(SOCKETS_LIST) == 0:
        connected = False


def send(message, alias):
    """Sends a message to the chat server."""
    global SOCKETS_LIST
    alias_found = False
    if connected == True:
        for socket in SOCKETS_LIST:
            if socket['alias'] == alias:
                socket['socket'].send(message.encode())
                alias_found = True
                break
        if alias_found == False:
            print(f"Alias '{alias}' not found. Please try again.")
    else: 
        print("\nNot connected to a chat. Please connect to a chat before sending a message.")


def receive_message():
    """Receives messages from the chat server."""
    global connected, SOCKETS_LIST, exit_flag
    while not exit_flag:

        if connected == True:
            for socket in SOCKETS_LIST:
                # TODO: MIGHT NEED TO REMOVE THIS TRY AND EXCEPT 
                try:
                    message = socket['socket'].recv(1024).decode()
                    if not message:
                        print(f"Disconnected from {socket['alias']}\n")
                        socket['socket'].close()
                        SOCKETS_LIST.remove(socket)
                        if len(SOCKETS_LIST) == 0:
                            connected = False
                    if message:
                        print(f"{socket['alias']}: {message}")
                except socket.error as errorMessage:
                    print(f"Failed to receive message. Error: {errorMessage}")
                    exit(1)
        else:
            pass


def wait_for_connection(server_port):
    """Waits for incoming chat connections."""
    global connected, SOCKETS_LIST, exit_flag, server_socket
    server_socket = start_socket(server_port)
    while not exit_flag: 
        try:
            chat_connection, client_address = server_socket.accept()
            # Prompt the user for an alias for the connection
            while True:
                response = input("Do you want to set an alias? (y/n): ").strip().lower()
                if response == "y" or response == "yes":
                    alias = input("Enter an alias: ")
                elif response == "n" or response == "no":
                    alias = client_address[0]
                else:
                    print(f"Invalid response. Please send yes(y) or no(n).")
                    # TODO: might need to try with "pass"
                    continue
                # Check if the alias already exists in SOCKETS_LIST
                alias_exists = any(socket['alias'] == alias for socket in SOCKETS_LIST)
                if not alias_exists:
                    break  # Exit the loop if the alias is unique
                print(f"Alias '{alias}' is already in use. Please choose a different alias.")
            SOCKETS_LIST.append({'socket': chat_connection, 'address': client_address, 'alias': alias})

        except socket.error as errorMessage:
            pass

def main():
    global exit_flag, connected, SOCKETS_LIST, server_address
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
            # handle help command
            if commandParts[0] == "help":
                print_commands()
            # handle connect command
            elif commandParts[0] == "connect":
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
            # handle send command
            elif commandParts[0] == "send":
                if connected == True:
                    # check if arguments are valid
                    if len(commandParts) < 3:
                        print("Expected format: send <host-IP or alias> <message>")
                    else:
                        alias = commandParts[1]
                        message = " ".join(commandParts[2:])
                        send(message, alias)
                else:
                    print("\nNot connected to a chat. Please connect to a chat before sending a message.")
            # handle disconnect command 
            elif commandParts[0] == "disconnect":
                # check if arguments are valid 
                if len(commandParts) != 2:
                    print("Expected format: disconnect <host-IP or alias>")
                else:
                    alias = commandParts[1]
                    disconnect(alias)
            # handle exit command
            elif commandParts[0] == "exit":
                exit_flag = True       # set exit flag to true
                server_socket.close()  # close server socket
                # close all sockets 
                for socket in SOCKETS_LIST:
                    socket['socket'].close()
                server_thread.join()    # wait for server thread to finish
                receive_thread.join()   # wait for receive thread to finish
                exit(0)                 # exit program gracefully
            # handle invalid command 
            else:
                print("Invalid command. Please enter a valid command from the list. \nType 'help' to see the list of commands.\n")


if __name__ == "__main__":
    main()