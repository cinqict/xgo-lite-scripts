import socket
from xgolib import XGO


dog = XGO(port='/dev/ttyAMA0', version="xgolite")


HOST = '0.0.0.0' #listen on all interfaces
PORT = 5000


# Simulated motor control functions
def move_forward():
    dog.move('x', 18)
    print("Robot moving forward...")


def stop_motors():
    dog.stop()
    print("Robot stopped.")


def turn_left():
    dog.turn(60)
    print("Robot turning left...")


def turn_right():
    dog.turn(-60)
    print("Robot turning right...")


# Start the server
while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse
        s.bind((HOST, PORT))
        s.listen()
        print(f"Robot server listening on {HOST}:{PORT}")


        conn, addr = s.accept()
        print(f"Connected by {addr}")
        with conn:
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        print("Client disconnected.")
                        break
                    command = data.decode().strip()
                    print(f"Received command: {command}")


                    if command == "forward":
                        move_forward()
                        conn.sendall(b"ACK: moving forward")
                    elif command == "stop":
                        stop_motors()
                        conn.sendall(b"ACK: stopped")
                    else:
                        conn.sendall(b"ERR: unknown command")


                except BrokenPipeError:
                    print("Client closed connection unexpectedly.")
                    break
