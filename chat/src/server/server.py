import concurrent.futures
import json
import socket
import threading

with open("../config/config.json") as config_file:
    data = json.load(config_file)

threadLock = threading.Lock()


class Server:
    def __init__(self, host="127.0.0.1", port=5050, buffer_size=1028, username_buffer_size=50):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()

        self.connected_clients = []
        self.buffer_size = buffer_size
        self.username_buffer_size = username_buffer_size

    def start(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            print("[Server started]....")
            _listen = executor.submit(self._listen_for_connection)

    def _listen_for_connection(self):
        while True:
            print("[Server listening for connections].... ")
            conn, addr = self.server_socket.accept()
            self.connected_clients.append(
                {
                    "connection": conn,
                    "address": addr,
                    "username": None
                }
            )
            print("[New connection established]....")

            conn_thread = threading.Thread(target=self._handle_connection, args=(conn, addr))
            conn_thread.start()

    def _handle_connection(self, conn, addr):
        print("[Server accepted new connection from {}]....".format(addr))
        is_username_set = False
        while True:
            if not is_username_set:
                username = conn.recv(self.username_buffer_size).decode("utf-8")
                threadLock.acquire()
                for client in self.connected_clients:
                    if client["connection"] is conn:
                        client["username"] = username
                threadLock.release()
                is_username_set = True

            buffer_size = int(conn.recv(self.buffer_size).decode("utf-8"))
            message = conn.recv(buffer_size)
            self._handle_message(message, conn)

    def _handle_message(self, _message, _from):
        _to = str(_message.decode("utf-8"))[:str(_message.decode("utf-8")).index("__")]
        threadLock.acquire()
        for client in self.connected_clients:
            if _from is client["connection"]:
                _message = str(_message.decode("utf-8")).replace(_to, client["username"]).encode("utf-8")

        for client in self.connected_clients:
            if str(client["username"]).strip().lower() == _to.lower():
                buffer_size = "{:<8}".format(len(_message.decode("utf-8")))
                client["connection"].send(buffer_size.encode("utf-8"))
                client["connection"].send(_message)
        threadLock.release()


if __name__ == "__main__":
    sev = Server(data["SERVER_IP"], data["SERVER_PORT"], data["BUFFER_SIZE"], data["BUFFER_SIZE"])
    sev.start()
