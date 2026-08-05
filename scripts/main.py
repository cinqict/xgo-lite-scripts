from xgolib import XGO
from detect_ping_pong_ball import main as detect_ball
import time

def init():
    # Initialize the robot on the default serial port
    # Use 'xgolite' or 'xgomini' depending on your hardware
    global dog
    dog = XGO(port='/dev/ttyAMA0', version="xgolite")

    # Optional: Auto-detect firmware version
    version = dog.read_firmware()
    if version == 'M':
        print("Detected XGO-MINI")
        dog = XGO(port='/dev/ttyAMA0', version="xgomini")
    else:
        print("Detected XGO-LITE")

def find_ball():
    detect_ball()


def move_forward():
    dog.move('x', 18)


def main():
    print("Can i pet that dog?")
    init()

if __name__ == "__main__":
    curses.wrapper(main)