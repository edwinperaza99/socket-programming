import threading
import socket
import sys
import time

# Global variables
EXIT_FLAG = False
CONNECTED = False
SOCKETS_LIST = []
ACTIVE_THREADS = []

# Get the hostname and IP address of the server
SERVER_ADDRESS = socket.gethostbyname(socket.gethostname())


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
        # check to see if alias was find in list
        if alias_found == False:
            print(f"Host IP '{host_ip}' not found. Please try again.")
    else:
        print("\nNot connected to a chat. Please connect to a chat before setting an alias.")


def start_socket(server_port):
    """Creates and configures a socket to listen for connections."""
    global server_socket
    # create a server socket
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as errorMessage:
        print(f"Failed to create client socket. Error: {errorMessage}")
        sys.exit(1)
    # bind the socket to the server address and port
    try:
        server_socket.bind(('', server_port))
    except socket.error as errorMessage:
        print(f"Failed to bind socket. Error: {errorMessage}")
        sys.exit(1)
    # No value passed to listen to allow for multiple connections
    server_socket.listen()
    return server_socket


def connect(serverIP, serverPort):
    """Attempts to connect to a chat server."""
    global CONNECTED, SOCKETS_LIST
    # create a client socket
    try:
        chat_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # give a maximum of 10 seconds to connect to the server
        chat_connection.settimeout(10)
    except socket.error as errorMessage:
        print(f"\nFailed to create client socket. Error: {errorMessage}")
        return
    # attempt to connect to the server
    try:
        chat_connection.connect((serverIP, serverPort))
        print(f"\nSuccessfully connected with {serverIP}\n")
        # Prompt the user for an alias
        while True:
            response = input("Do you want to set an alias? (y/n): ").strip().lower()
            if response == "y" or response == "yes":
                alias = input("Enter an alias: ")
            # if no alias is passed, we default alias to the socket IP address
            elif response == "n" or response == "no":
                alias = serverIP
            else:
                print(f"Invalid response. Please send yes(y) or no(n).")
                continue
            # Check if the alias already exists in SOCKETS_LIST
            alias_exists = any(socket_info['alias'] == alias for socket_info in SOCKETS_LIST)
            if not alias_exists:
                break  # Exit the loop if the alias is unique
            print(f"Alias '{alias}' is already in use. Please choose a different alias.")

        # Add the new socket to the SOCKETS_LIST
        new_socket_info = {'socket': chat_connection, 'address': (serverIP, serverPort), 'alias': alias, 'active': True}
        SOCKETS_LIST.append(new_socket_info)
        # If we did not have any connections before, set CONNECTED to True
        if CONNECTED == False:
            CONNECTED = True

        # Create a new thread for each client to handle message reception
        host_thread = threading.Thread(target=receive_message, args=(new_socket_info,))
        host_thread.start()
        # Add the information of the thread to the ACTIVE_THREADS list
        ACTIVE_THREADS.append({'thread': host_thread, 'alias': alias})
    except socket.error as errorMessage:
        print(f"\nFailed to connect to the client. Error: {errorMessage}")
        chat_connection.close()
        return
    

def disconnect(alias, alias_found = False):
    """Disconnects from a chat server."""
    global CONNECTED, SOCKETS_LIST
    for socket_info in SOCKETS_LIST:
        # find socket on the list that we want to disconnect from 
        if socket_info['alias'] == alias or socket_info['address'][0] == alias:
            print(f"\nDisconnected from {socket_info['alias']}\n")
            socket_info['socket'].close()       # close the socket
            socket_info['active'] = False       # set active flag to false to remove socket and thread from list
            alias_found = True
            break
    # check to see if alias was found in list
    if alias_found == False:
        print(f"Alias '{alias}' not found. Please try again.")
    # check if there are any active connections left and set CONNECTED to false if there are none
    if len(SOCKETS_LIST) == 0:
        CONNECTED = False


def send(message, alias):
    """Sends a message to a chat server."""
    global SOCKETS_LIST
    alias_found = False
    if CONNECTED == True:
        for socket_info in SOCKETS_LIST:
            # alias is either the alias or the IP address of the socket
            if socket_info['alias'] == alias or socket_info['address'][0] == alias:
                # encode and send the message to the socket
                socket_info['socket'].send(message.encode())
                print(f"Message '{message}' sent to {socket_info['alias']}")
                alias_found = True
                break
        # check to see if alias was found in list
        if alias_found == False:
            print(f"Alias '{alias}' not found. Please try again.")
    else: 
        print("\nNot connected to a chat. Please connect to a chat before sending a message.")



def receive_message(socket_info):
    """Receives messages from the chat server."""
    global CONNECTED, SOCKETS_LIST, EXIT_FLAG
    # run thread until exit flag is set or socket is no longer active
    while not EXIT_FLAG and socket_info['active']:
        if CONNECTED == True:
            try:
                # decode and print the message received from the socket
                message = socket_info['socket'].recv(1024).decode()
                if message:
                    print(f'\nMessage "{message}" received from {socket_info["alias"]}')
                # If the received message is empty, it's a sign of disconnection.
                elif not message:
                    if socket_info['active'] == True:
                        disconnect(socket_info['alias'], True)
            # Handle disconnections from socket
            except (ConnectionResetError, ConnectionAbortedError) as errorMessage:
                if socket_info['active'] == True:
                    disconnect(socket_info['alias'], True)
            except socket.error as errorMessage:
                pass


def wait_for_connection(server_port):
    """Waits for incoming chat connections."""
    global CONNECTED, SOCKETS_LIST, EXIT_FLAG, server_socket
    server_socket = start_socket(server_port)
    # run thread until exit flag is set
    while not EXIT_FLAG: 
        try:
            # accept incoming connection
            chat_connection, client_address = server_socket.accept()
            print(f"\nAccepted connection with {client_address[0]}.\n")
            # set alias as default, this can later be modified by user
            new_socket_info = {'socket': chat_connection, 'address': client_address, 'alias': client_address[0], 'active': True}
            SOCKETS_LIST.append(new_socket_info)
            CONNECTED = True   # set CONNECTED to true if we have at least one connection

            # Create a new thread for each client to handle message reception
            host_thread = threading.Thread(target=receive_message, args=(new_socket_info,))
            host_thread.start()
            # Add the information of the thread to the ACTIVE_THREADS list
            ACTIVE_THREADS.append({'thread': host_thread, 'alias': client_address[0]})
        except socket.error as errorMessage:
            pass


def handle_threads():
    """Handles all active threads."""
    global ACTIVE_THREADS, SOCKETS_LIST
    # run thread until exit flag is set
    while not EXIT_FLAG:
        # iterate through all sockets and threads to check if any have been disconnected
        for socket_info in SOCKETS_LIST:
            # if socket is no longer active, join the thread and remove it from the list
            if socket_info['active'] == False:
                for thread_info in ACTIVE_THREADS:
                    # match the thread to the socket using the alias
                    if thread_info['alias'] == socket_info['alias'] or thread_info['alias'] == socket_info['address'][0]:
                        thread_info['thread'].join()
                        ACTIVE_THREADS.remove(thread_info)
                SOCKETS_LIST.remove(socket_info)

def main():
    """Main function in charge of handling user commands."""
    global EXIT_FLAG, CONNECTED, SOCKETS_LIST, SERVER_ADDRESS, server_socket
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

    # start thread to handle closing of threads and removing sockets from list
    thread_handler = threading.Thread(target=handle_threads)
    thread_handler.start()

    # start thread to listen for incoming connections
    server_thread = threading.Thread(target=wait_for_connection, args=(server_port,))
    server_thread.start()

    print(f"\nChat running at {SERVER_ADDRESS} on port {server_port}")
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
                    print("\nNot connected to a chat. Please connect to a chat before sending a message.")
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
                print("\nExiting chat program...\n")
                server_socket.close()  # close server socket
                # Disconnect from all active sockets
                for socket_info in SOCKETS_LIST:
                    if socket_info['active'] == True:
                        disconnect(socket_info['alias'], True)
                # wait for 2 second to allow threads to finish
                time.sleep(2)
                EXIT_FLAG = True       # set exit flag to true
                server_thread.join()    # wait for server thread to finish
                thread_handler.join()   # wait for thread handler thread to finish
                print("\nChat program terminated. Goodbye!\n")
                sys.exit(0)                 # exit program gracefully
            # handle invalid command 
            else:
                print("Invalid command. Please enter a valid command from the list. \nType 'help' to see the list of commands.\n")


if __name__ == "__main__":
    main()