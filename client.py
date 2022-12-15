import socket
import concurrent.futures
import json

with open("config.json") as config_file:
    data = json.load(config_file)

HOST = data["SERVER_IP"]
PORT = data["SERVER_PORT"]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

print("[Connected to server]")


def receive_message():
    while True:
        recv_msg = client_socket.recv(1028).decode("utf-8")
        print("Received message: ", recv_msg)


with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    _received = executor.submit(receive_message)

    while True:
        msg = str(input(">> ")).encode("utf-8")
        client_socket.send(msg)
