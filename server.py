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
    threadLock.acquire()
    print("[Server Broadcasting message to {} clients]....".format(len(connected_clients)))
    for client in connected_clients:
        if client is not _from:
            buffer_size = "{:<8}".format(len(_message.decode("utf-8")))
            client.send(buffer_size.encode("utf-8"))
            client.send(_message)
    threadLock.release()


def handle_connection(conn, addr):
    print("[Server accepted new connection from {}]....".format(addr))
    while True:
        buffer_size = int(conn.recv(data["BUFFER_SIZE"]).decode("utf-8"))
        message = conn.recv(buffer_size)
        handle_message(message, conn)


def listen_for_connection():
    while True:
        print("[Server listening for connections].... ")
        conn, addr = server_socket.accept()
        connected_clients.append(conn)
        print("[New connection established]....")

        conn_thread = threading.Thread(target=handle_connection, args=(conn, addr))
        conn_thread.start()


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        print("[Server started]....")
        _listen = executor.submit(listen_for_connection)


if __name__ == "__main__":
    main()
