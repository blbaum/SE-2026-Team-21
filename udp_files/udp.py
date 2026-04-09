import socket
# import threading

START_GAME_CODE: int = 202
END_GAME_CODE: int = 221
RED_SCORE_CODE: int = 53
GREEN_SCORE_CODE: int = 43

class UDP:
    def __init__(self, send_port=7500, receive_port=7501, receive_ip="0.0.0.0", send_ip="127.0.0.1"):
        self.receive_port = receive_port
        self.receive_sock = None
        self.receive_ip = receive_ip

        self.send_ip = send_ip
        self.send_port = send_port
        self.send_address = (self.send_ip, self.send_port)
        self.send_sock = None

        self.buffer_size = 1024

    def setup_sockets(self):
        self.receive_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.receive_sock.bind((self.receive_ip, self.receive_port))

        self.send_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        print(f"Receive socket listening at: {self.receive_ip}:{self.receive_port}")
        print(f"Send socket sending to: {self.send_ip}:{self.receive_port}")

    def update_server_ip(self, new_ip):
        self.send_ip = new_ip
        self.send_address = (self.send_ip, self.receive_port)
        print(f"Send address updated to {self.send_ip}:{self.receive_port}")

    def send_data(self, data):
        if self.send_sock is None:
            print("Setup UDP to send data")
            return

        encoded_data = str.encode(str(data))
        self.send_sock.sendto(encoded_data, self.send_address)
        print(f"Sent: {encoded_data.decode()}")
        print(f"To: {self.send_ip}:{self.receive_port}")
    
    def send_start_code(self):
        self._send_data(START_GAME_CODE)
    
    def send_end_code(self):
        self._send_data(END_GAME_CODE)
    
    def send_red_score_code(self):
        self._send_data(RED_SCORE_CODE)
    
    def send_green_score_code(self):
        self._send_data(GREEN_SCORE_CODE)


    def close_sockets(self):
        try:
            if(self.receive_sock != None):
                self.receive_sock.close()
                print("Receive socket closed")
            if(self.send_sock != None):
                self.send_sock.close()
                print("Send socket closed")
        except Exception as e:
            print(e)

    def get_server_ip(self):
        return self.send_ip