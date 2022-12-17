import socket
import concurrent.futures
import json

with open("../config/config.json") as config_file:
    data = json.load(config_file)


class Client:
    def __init__(self, server_address="127.0.0.1", server_port=5050, buffer_size=1028):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_address, server_port))
        self.buffer_size = buffer_size

    def start(self):

        print("[Connected to server]")

        username = str(input("Enter username: "))
        self._send_username(username=username)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            _received = executor.submit(self._receive_message)

            while True:
                msg = str(input(">> ")).strip()
                buffer_size = "{:<8}".format(len(msg))
                if int(buffer_size) > 1:
                    self.client_socket.send(buffer_size.encode("utf-8"))
                    self.client_socket.send(msg.encode("utf-8"))

    def _send_username(self, username: str):
        self.client_socket.send(username.encode("utf-8"))

    def _receive_message(self, ):
        while True:
            buffer_size = self.client_socket.recv(data["BUFFER_SIZE"]).decode("utf-8")
            recv_msg = self.client_socket.recv(int(buffer_size.strip())).decode("utf-8")
            msg = "{}: {}".format(recv_msg[:recv_msg.index("__")], recv_msg[recv_msg.index("__") + 2:])
            print(msg)


if __name__ == "__main__":
    cl = Client(data["SERVER_IP"], data["SERVER_PORT"], data["BUFFER_SIZE"])
    cl.start()
