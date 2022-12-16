import socket
import concurrent.futures
import json

with open("config.json") as config_file:
    data = json.load(config_file)

HOST = data["SERVER_IP"]
PORT = data["SERVER_PORT"]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))


def receive_message():
    while True:
        buffer_size = client_socket.recv(data["BUFFER_SIZE"]).decode("utf-8")
        recv_msg = client_socket.recv(int(buffer_size.strip())).decode("utf-8")
        msg = "{}: {}".format(recv_msg[:recv_msg.index("__")], recv_msg[recv_msg.index("__") + 2:])
        print(msg)


def send_username(username: str):
    client_socket.send(username.encode("utf-8"))


def main():
    print("[Connected to server]")

    username = str(input("Enter username: "))
    send_username(username=username)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        _received = executor.submit(receive_message)

        while True:
            msg = str(input(">> ")).strip()
            buffer_size = "{:<8}".format(len(msg))
            if int(buffer_size) > 1:
                client_socket.send(buffer_size.encode("utf-8"))
                client_socket.send(msg.encode("utf-8"))


if __name__ == "__main__":
    main()
