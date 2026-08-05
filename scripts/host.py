import socket
from time import sleep


HOST = '192.168.1.75'
PORT = 5000


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'forward')
    sleep(2)
    s.sendall(b'right')
    sleep(2)
    s.sendall(b'stop')
    ack = s.recv(1024).decode()
    print(f"Robot says: {ack}")
