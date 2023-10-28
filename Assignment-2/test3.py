import socket
import threading

class ChatClient:
    def __init__(self):
        self.exit_flag = False
        self.connected = False
        self.chat_connection = None
        self.address = None
        self.host_ip = None
        self.server_socket = None
        self.server_address = socket.gethostbyname(socket.gethostname())

    def start_socket(self, server_port):
        """Creates and configures a socket to listen for connections."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('', server_port))
            self.server_socket.listen(1)
        except socket.error as errorMessage:
            print(f"Socket setup error: {errorMessage}")
            exit(1)

    def connect(self, serverIP, serverPort):
        """Attempts to connect to a chat server."""
        try:
            self.chat_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.chat_connection.connect((serverIP, serverPort))
            print(f"\nSuccessfully connected with {serverIP}\n")
            self.connected = True
        except socket.error as errorMessage:
            print(f"\nFailed to connect to client. Error: {errorMessage}")

    def disconnect(self):
        """Disconnects from the chat server."""
        self.connected = False
        if self.address is None:
            print(f"\nDisconnected from {self.host_ip}\n")
        else:
            print(f"Disconnected from {self.address}\n")
        self.chat_connection.close()

    def send(self, message):
        """Sends a message to the connected chat server."""
        if self.connected:
            if self.chat_connection:
                self.chat_connection.send(message.encode())
                print(f"Message \"{message}\" sent")
        else:
            print("\nNot connected to a chat. Please connect to a chat before sending a message.")

    def receive_message(self):
        """Receives messages from the chat server."""
        while not self.exit_flag:
            try:
                if self.connected:
                    message = self.chat_connection.recv(1024).decode()
                    if not message:
                        # If the received message is empty, it's a sign of disconnection.
                        if self.address is not None:
                            print(f"\n\nHost at {self.address} disconnected\n\nEnter command: ", end="")
                            self.address = None
                        else:
                            print(f"\n\nHost at {self.host_ip} disconnected\n\nEnter command: ", end="")
                            self.host_ip = None
                        self.chat_connection.close()
                        self.connected = False
                    elif message:
                        print(f"\nMessage \"{message}\" received \n\nEnter command: ", end="")
                else:
                    pass
            except (ConnectionResetError, ConnectionAbortedError) as errorMessage:
                if self.address is not None:
                    print(f"\n\nHost at {self.address} disconnected\n\nEnter command: ", end="")
                self.chat_connection.close()
                self.connected = False
            except socket.error as errorMessage:
                self.chat_connection.close()
                self.connected = False

    def wait_for_connection(self, server_port):
        """Waits for incoming chat connections."""
        while not self.exit_flag:
            if not self.connected:
                try:
                    self.chat_connection, client_address = self.server_socket.accept()
                    self.address = client_address[0]
                    print(f"\n\nAccepted connection with {self.address}\n\nEnter command: ", end="")
                    self.connected = True
                except socket.error as errorMessage:
                    pass
            else:
                pass

    def run(self):
        # ask for port number to connect to and check that it is in the range of 10,000 to 20,000
        while True:
            try:
                server_port = int(input("Enter server port number: "))
                if 10000 <= server_port <= 20000:
                    break
                else:
                    print("Port number must be between 10,000 and 20,000.")
            except ValueError:
                print("Invalid input. Port number must be an integer.")

        # start thread to listen for incoming connections
        server_thread = threading.Thread(target=self.wait_for_connection, args=(server_port,))
        server_thread.start()

        # start thread to receive messages
        receive_thread = threading.Thread(target=self.receive_message)
        receive_thread.start()

        print(f"\nChat running at {self.server_address} on port {server_port}")

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
                if commandParts[0] == "help":
                    self.print_commands()
                elif commandParts[0] == "connect":
                    if not self.connected:
                        if len(commandParts) != 3:
                            print("Expected format: connect <IP address> <port number>")
                        else:
                            host_port = int(commandParts[2])
                            if 10000 <= host_port <= 20000:
                                self.host_ip = commandParts[1]
                                self.connect(self.host_ip, host_port)
                            else:
                                print("Port number must be between 10,000 and 20,000.")
                    else:
                        print("Already connected to a chat. Please disconnect before connecting to another chat.")
                elif commandParts[0] == "send":
                    if self.connected:
                        if len(commandParts) < 2:
                            print("Command message was received, but no message was attached to command.")
                            print("Expected format: send <message>")
                        else:
                            message = ' '.join(commandParts[1:])
                            self.send(message)
                    else:
                        print("Not connected to a chat. Please connect to a chat before sending a message.\n")
                elif commandParts[0] == "disconnect":
                    if self.connected:
                        self.disconnect()
                    else:
                        print("Not connected to a chat. Disconnect command is not available.\n")
                elif commandParts[0] == "exit":
                    self.exit_flag = True
                    if self.server_socket:
                        self.server_socket.close()
                    if self.chat_connection:
                        self.chat_connection.close()
                    server_thread.join()
                    receive_thread.join()
                    exit(0)
                else:
                    print("Invalid command. Please enter a valid command from the list.\nType 'help' to see the list of commands.\n")

    def print_commands(self):
        if self.connected is False:
            print("\nList of commands:")
            print("connect <IP address> <port number>")
            print("help")
            print("exit\n")
        elif self.connected is True:
            print("\nList of commands:")
            print("send <message>")
            print("disconnect")
            print("help")
            print("exit\n")

if __name__ == "__main__":
    chat_client = ChatClient
    chat_client.run(chat_client)
