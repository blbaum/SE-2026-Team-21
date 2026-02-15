import socket

class UDP:
    local_ip = "0.0.0.0"
    buffer_size = 1024

    def __init__(self, client=7500, server=7501):
        self.server_port = server
        self.server_sock = None
        self.server_ip = "127.0.0.1"
        self.server_address = (self.server_ip, self.server_port)

        self.client_port = client
        self.client_sock = None

    def start(self):
        self.server_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.server_sock.bind((UDP.local_ip, self.server_port))

        self.client_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        print(f"Server listening at: {UDP.local_ip}:{self.server_port}")
        print(f"Client sending from port: {self.client_port} to IP: ")

    def update_server_address(self, new_ip):
        self.server_ip = new_ip
        self.server_address = (self.server_ip, self.server_port)
        print(f"Server address updated to {self.server_ip}:{self.server_port}")

    def send_data(self, data):
        if self.client_sock is None:
            print("Setup UDP to send data")
            return

        encoded_data = str.encode(data)
        self.client_sock.sendto(encoded_data, self.server_address)
        print(f"Client Sent: {encoded_data.decode()}")
