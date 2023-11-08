import threading
import socket

# Global variables
EXIT_FLAG = False
CONNECTED = False
SOCKETS_LIST = []
ACTIVE_THREADS = []

# Get the hostname and IP address of the server
hostname = socket.gethostname()
server_address = socket.gethostbyname(hostname)


# TODO: I think this is done
def print_commands():
    """Prints a list of available commands based on the connection status."""
    global CONNECTED
    print("\nList of commands:") 
    print("connect <IP address> <port number>")
    if CONNECTED == True:
        print("send <host-IP or alias> <message>")
        print("disconnect <host-IP or alias>")
        print("set_alias <host-IP> <alias>")
        print("list_connections")
    print("help")
    print("exit\n")


def list_connections():
    """Lists all connections with their aliases."""
    global SOCKETS_LIST, CONNECTED
    if CONNECTED == True:
        print("\nList of connections:")
        for socket_info in SOCKETS_LIST:
            print(f"IP:{socket_info['address'][0]}\tAlias: {socket_info['alias']}")
    else:
        print("\nNot connected to a chat. Please connect to a chat before listing connections.")


def set_alias(host_ip, alias):
    """Sets the alias for a connection."""
    global SOCKETS_LIST
    alias_found = False
    if CONNECTED == True:
        for socket_info in SOCKETS_LIST:
            if socket_info['alias'] == host_ip or socket_info['address'][0] == host_ip:
                socket_info['alias'] = alias
                print(f"Alias for {socket_info['address'][0]} set to {socket_info['alias']}")
                alias_found = True
                break
        if alias_found == False:
            print(f"Host IP '{host_ip}' not found. Please try again.")
    else:
        print("\nNot connected to a chat. Please connect to a chat before setting an alias.")


# TODO: I think this is done
def start_socket(server_port):
    """Creates and configures a socket to listen for connections."""
    global server_socket
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
    server_socket.listen()
    return server_socket


def connect(serverIP, serverPort):
    """Attempts to connect to a chat server."""
    global CONNECTED, SOCKETS_LIST
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
            alias_exists = any(socket_info['alias'] == alias for socket_info in SOCKETS_LIST)
            if not alias_exists:
                break  # Exit the loop if the alias is unique
            print(f"Alias '{alias}' is already in use. Please choose a different alias.")

        new_socket_info = {'socket': chat_connection, 'address': (serverIP, serverPort), 'alias': alias, 'active': True}
        SOCKETS_LIST.append(new_socket_info)
        if CONNECTED == False:
            CONNECTED = True

        # Create a new thread for each client to handle message reception
        host_thread = threading.Thread(target=receive_message, args=(new_socket_info,))
        host_thread.start()
        ACTIVE_THREADS.append({'thread': host_thread, 'alias': alias})
    except socket.error as errorMessage:
        print(f"\nFailed to connect to the client. Error: {errorMessage}")
        chat_connection.close()
        return
    

def disconnect(alias):
    """Disconnects from the chat server."""
    global CONNECTED, SOCKETS_LIST
    alias_found = False
    for socket_info in SOCKETS_LIST:
        if socket_info['alias'] == alias or socket_info['address'][0] == alias:
            print(f"Disconnected from {socket_info['alias']}\n")
            socket_info['socket'].close()
            socket_info['active'] = False
            SOCKETS_LIST.remove(socket_info)
            for thread_info in ACTIVE_THREADS:
                if thread_info['alias'] == alias:
                    thread_info['thread'].join()
                    ACTIVE_THREADS.remove(thread_info)
            alias_found = True
            break
    if alias_found == False:
        print(f"Alias '{alias}' not found. Please try again.")
    if len(SOCKETS_LIST) == 0:
        CONNECTED = False


def send(message, alias):
    """Sends a message to the chat server."""
    global SOCKETS_LIST
    alias_found = False
    if CONNECTED == True:
        for socket_info in SOCKETS_LIST:
            if socket_info['alias'] == alias or socket_info['address'][0] == alias:
                socket_info['socket'].send(message.encode())
                print(f"Message '{message}' sent to {socket_info['alias']}")
                alias_found = True
                break
        if alias_found == False:
            print(f"Alias '{alias}' not found. Please try again.")
    else: 
        print("\nNot connected to a chat. Please connect to a chat before sending a message.")


# TODO: I might have to run one of these threads for each socket
def receive_message(socket_info):
    """Receives messages from the chat server."""
    global CONNECTED, SOCKETS_LIST, EXIT_FLAG
    # TODO: need to test this since we are removing exit flag 
    while not EXIT_FLAG and socket_info['active']:
        if CONNECTED == True:
            try:
                message = socket_info['socket'].recv(1024).decode()
                if message:
                    print(f'\nMessage "{message}" received from {socket_info["alias"]}')
                elif not message:
                    print(f"Disconnected from {socket_info['alias']}\n")
                    socket_info['socket'].close()
                    SOCKETS_LIST.remove(socket_info)
                    if len(SOCKETS_LIST) == 0:
                        CONNECTED = False
            except (ConnectionResetError, ConnectionAbortedError) as errorMessage:
                print(f"Disconnected from {socket_info['alias']}\n")
                socket_info['socket'].close()
                SOCKETS_LIST.remove(socket_info)
                if len(SOCKETS_LIST) == 0:
                    CONNECTED = False
            except socket.error as errorMessage:
                socket_info['socket'].close()
                SOCKETS_LIST.remove(socket_info)
                if len(SOCKETS_LIST) == 0:
                    CONNECTED = False


def wait_for_connection(server_port):
    """Waits for incoming chat connections."""
    global CONNECTED, SOCKETS_LIST, EXIT_FLAG, server_socket
    server_socket = start_socket(server_port)
    while not EXIT_FLAG: 
        try:
            chat_connection, client_address = server_socket.accept()
            print(f"\nAccepted connection with {client_address[0]}.\n")
            new_socket_info = {'socket': chat_connection, 'address': client_address, 'alias': client_address[0], 'active': True}
            SOCKETS_LIST.append(new_socket_info)
            CONNECTED = True

            # Create a new thread for each client to handle message reception
            host_thread = threading.Thread(target=receive_message, args=(new_socket_info,))
            host_thread.start()
            ACTIVE_THREADS.append({'thread': host_thread, 'alias': client_address[0]})
        except socket.error as errorMessage:
            pass

def main():
    global EXIT_FLAG, CONNECTED, SOCKETS_LIST, server_address
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

    # TODO: remove this comment 
    # start thread to receive messages
    # receive_thread = threading.Thread(target=receive_message)
    # receive_thread.start()

    print(f"\nChat running at {server_address} on port {server_port}")
    # print initial command list
    print_commands()

    # loop to handle main program commands 
    while True:
        try:
            command = input("Enter command: \n")
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
                if CONNECTED == True:
                    # check if arguments are valid
                    if len(commandParts) < 3:
                        print("Expected format: send <host-IP or alias> <message>")
                    else:
                        alias = commandParts[1]
                        message = " ".join(commandParts[2:])
                        send(message, alias)
                else:
                    print("\nNot CONNECTED to a chat. Please connect to a chat before sending a message.")
            # handle disconnect command 
            elif commandParts[0] == "disconnect":
                # check if arguments are valid 
                if len(commandParts) != 2:
                    print("Expected format: disconnect <host-IP or alias>")
                else:
                    alias = commandParts[1]
                    disconnect(alias)
            # handle set_alias command
            elif commandParts[0] == "set_alias":
                # check if arguments are valid 
                if len(commandParts) != 3:
                    print("Expected format: set_alias <host-IP or alias> <alias>")
                else:
                    set_alias(commandParts[1], commandParts[2])
            # handle list_connections command
            elif commandParts[0] == "list_connections":
                list_connections()
            # handle exit command
            elif commandParts[0] == "exit":
                EXIT_FLAG = True       # set exit flag to true
                server_socket.close()  # close server socket
                # close all sockets 
                for socket_info in SOCKETS_LIST:
                    socket_info['socket'].close()
                server_thread.join()    # wait for server thread to finish
                # TODO: remove this comment 
                # receive_thread.join()   # wait for receive thread to finish
                exit(0)                 # exit program gracefully
            # handle invalid command 
            else:
                print("Invalid command. Please enter a valid command from the list. \nType 'help' to see the list of commands.\n")


if __name__ == "__main__":
    main()