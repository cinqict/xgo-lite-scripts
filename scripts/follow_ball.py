from xgolib import XGO
import cv2
import numpy as np
import time

from grab_object import grab_object

# ---------------------------------------------------------------------
# Color presets (HSV). Tune these to your ball + lighting.
# Use a tool like https://github.com/alieldinayman/HSV-Color-Picker
# or the trackbar script further down to dial these in live.
# ---------------------------------------------------------------------
COLOR_PRESETS = {
    "orange": {
        "lower": np.array([5, 120, 120]),
        "upper": np.array([20, 255, 255]),
    },
    "white": {
        "lower": np.array([0, 0, 200]),
        "upper": np.array([180, 40, 255]),
    },
    "red": {
        "lower": np.array([170, 120, 80]),
        "upper": np.array([180, 255, 255]),
    },
    "green": {
        "lower": np.array([35, 80, 80]),
        "upper": np.array([85, 255, 255]),
    },
}


BALL_DIAMETER_MM = 20.0

# Approximate focal length in pixels — calibrate this for your camera.
FOCAL_LENGTH_PX = 600.0

MIN_RADIUS_PX = 6
MIN_CIRCULARITY = 0.55

CRAWL_DISTANCE_MM = 400
BALL_GRAB_DISTANCE_MM = 140
FRAME_CENTER_X = 320
CENTER_TOLERANCE_X = 25
MAX_MISSED_FRAMES = 20

STATE = "INIT"
HAS_BALL = False
dog = None
cap = None
color_name = "green"

def set_state(new_state):
    global STATE
    print(f"STATE: {STATE} -> {new_state}")
    STATE = new_state


def init():
    global dog

    dog = XGO(port='/dev/ttyAMA0', version="xgolite")

    version = dog.read_firmware()
    if version == 'M':
        print("Detected XGO-MINI")
        dog = XGO(port='/dev/ttyAMA0', version="xgomini")
    else:
        print("Detected XGO-LITE")

    dog.stop()
    set_state("FIND_BALL")


def detect_ball(frame, color_name: str):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    preset = COLOR_PRESETS[color_name]
    mask = cv2.inRange(hsv, preset["lower"], preset["upper"])

    # Clean up the mask.
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    best = None
    best_score = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 30:
            continue

        (x, y), radius = cv2.minEnclosingCircle(cnt)
        if radius < MIN_RADIUS_PX:
            continue

        circle_area = np.pi * (radius ** 2)
        circularity = area / circle_area if circle_area > 0 else 0
        if circularity < MIN_CIRCULARITY:
            continue

        score = circularity * area
        if score > best_score:
            best_score = score
            best = (int(x), int(y), int(radius))

    return best, mask


def estimate_distance_mm(radius_px):
    if radius_px <= 0:
        return None

    return (BALL_DIAMETER_MM / 2) * FOCAL_LENGTH_PX / radius_px


def find_ball():
    print("Searching for ball. Press 'c' to switch color preset, 'q' to quit.\n")

    while STATE == "FIND_BALL":
        ret, frame = cap.read()
        if not ret:
            print("Frame grab failed.")
            set_state("STOP")
            break


        result, mask = detect_ball(frame, color_name)

        if result:
            x, y, r = result
            dist = estimate_distance_mm(r)
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
            cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)
            label = f"{color_name} ball  r={r}px"
            if dist:
                label += f"  ~{dist / 10:.1f}cm"
            cv2.putText(frame, label, (x - 40, y - r - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            print("Found ball:", x, y, "r:", r, "dist:", dist, "mm\n")
        else:
            cv2.putText(frame, f"Searching ({color_name})...", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            print("No ball found. Looking around...\n")
            # dog.turn(20)

        cv2.imshow("XGO Ball Detection", frame)
        cv2.imshow("Mask", mask)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            set_state("STOP")
            break

        if result:
            dog.stop()
            set_state("MOVE_TO_BALL")
            break

def move_to_ball():

    missed_frames = 0
    crawling = False

    print("Moving to ball\n")

    while STATE == "MOVE_TO_BALL":
        ret, frame = cap.read()
        if not ret:
            print("Frame grab failed.\n")
            set_state("STOP")
            break

        result, mask = detect_ball(frame, color_name)
        if not result:
            missed_frames += 1
            print(f"Missed ball frame {missed_frames}/{MAX_MISSED_FRAMES}\n")
            cv2.imshow("XGO Ball Detection", frame)
            cv2.imshow("Mask", mask)
            cv2.waitKey(1)

            if missed_frames >= MAX_MISSED_FRAMES:
                dog.stop()
                print("Lost ball, searching again.\n")
                set_state("FIND_BALL")
                break

            continue

        missed_frames = 0

        x, y, r = result
        dist = estimate_distance_mm(r)

        cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
        cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)
        label = f"{color_name} ball  r={r}px"
        if dist:
            label += f"  ~{dist / 10:.1f}cm"
        cv2.putText(frame, label, (x - 40, y - r - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        print("Moving toward ball:", x, y, "r:", r, "dist:", dist, "mm\n")

        cv2.imshow("XGO Ball Detection", frame)
        cv2.imshow("Mask", mask)
        cv2.waitKey(1)

        # frame_center_x = frame.shape[1] // 2
        if x < FRAME_CENTER_X - CENTER_TOLERANCE_X:
            print("turn left\n")
            if(crawling):
                dog.turn(5)
            else:
                dog.turn(10)
        elif x > FRAME_CENTER_X + CENTER_TOLERANCE_X:
            print("turn right\n")
            if(crawling):
                dog.turn(-5)
            else:
                dog.turn(-10)
        elif dist is not None and dist > CRAWL_DISTANCE_MM:
            print("move forward\n")
            dog.move('x', 10)
        elif dist is not None and dist > BALL_GRAB_DISTANCE_MM:
            print("crawl forward\n")
            if(not crawling):
                dog.pace('slow')
                # dog.translation('z', -18)
                dog.attitude('p', 15)
                crawling = True
            else:
                crawl_to_ball()
        else:
            print("Ball is close enough.\n")
            dog.stop()
            set_state("GRAB_BALL")
            break



def crawl_to_ball():
    print("Crawling to ball\n")
    dog.move('x', 5)

def grab_ball():
    global HAS_BALL

    print("Grabbing ball\n")
    dog.stop()

    grab_object()

    HAS_BALL = True
    set_state("DANCE")

def dance():
    print("Dancing\n")
    #
    dog.stop()
    set_state("STOP")

def main():
    print("Can i pet that dog?\n")
    global cap
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Could not open camera.")
        set_state("STOP")
        return

    cv2.namedWindow("XGO Ball Detection")
    cv2.namedWindow("Mask")

    try:
        while True:
            if STATE == "INIT":
                init()

            elif STATE == "FIND_BALL":
                find_ball()

            elif STATE == "MOVE_TO_BALL":
                move_to_ball()

            elif STATE == "GRAB_BALL":
                grab_ball()

            elif STATE == "DANCE":
                if HAS_BALL:
                    dance()
                    # throw_ball_upwards()
                else:
                    set_state("FIND_BALL")

            elif STATE == "STOP":
                if dog:
                    dog.stop()
                break

            time.sleep(0.1)

    finally:
        if dog:
            dog.stop()

        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()

    print("Goodbye\n")


if __name__ == "__main__":
    main()