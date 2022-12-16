import concurrent.futures
import json
import socket
import threading

with open("config.json") as config_file:
    data = json.load(config_file)

HOST = data["SERVER_IP"]
PORT = data["SERVER_PORT"]

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

connected_clients = []

threadLock = threading.Lock()


def handle_message(_message, _from):
    _to = str(_message.decode("utf-8"))[:str(_message.decode("utf-8")).index("__")]
    threadLock.acquire()
    for client in connected_clients:
        if _from is client["connection"]:
            _message = str(_message.decode("utf-8")).replace(_to, client["username"]).encode("utf-8")

    for client in connected_clients:
        if str(client["username"]).strip().lower() == _to.lower():
            buffer_size = "{:<8}".format(len(_message.decode("utf-8")))
            client["connection"].send(buffer_size.encode("utf-8"))
            client["connection"].send(_message)
    threadLock.release()


def handle_connection(conn, addr):
    print("[Server accepted new connection from {}]....".format(addr))
    is_username_set = False
    while True:
        if not is_username_set:
            username = conn.recv(data["USERNAME_BUFFER_SIZE"]).decode("utf-8")
            threadLock.acquire()
            for client in connected_clients:
                if client["connection"] is conn:
                    client["username"] = username
            threadLock.release()
            is_username_set = True

        buffer_size = int(conn.recv(data["BUFFER_SIZE"]).decode("utf-8"))
        message = conn.recv(buffer_size)
        handle_message(message, conn)


def listen_for_connection():
    while True:
        print("[Server listening for connections].... ")
        conn, addr = server_socket.accept()
        connected_clients.append(
            {
                "connection": conn,
                "address": addr,
                "username": None
            }
        )
        print("[New connection established]....")

        conn_thread = threading.Thread(target=handle_connection, args=(conn, addr))
        conn_thread.start()


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        print("[Server started]....")
        _listen = executor.submit(listen_for_connection)


if __name__ == "__main__":
    main()
