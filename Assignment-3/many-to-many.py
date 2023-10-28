import threading
import socket

class Chat:
    def __init__(self, server_port):
        self.exit_flag = False
        self.connected = False
        self.chat_connection = None
        self.address = None
        self.host_ip = None
        server_port = server_port
        self.server_socket = None
        self.server_address = socket.gethostbyname(socket.gethostname())

if __name__ == "__main__":
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
    
    # start first chat instance
    chat1 = Chat(server_port)

