"""
Line Follower for XGO Lite
----------------------------
Uses the onboard/USB camera to find a line on the floor and steers the
robot dog to follow it, using xgolib's move()/turn() motion API.

Hardware assumption:
    XGO Lite connected over its onboard serial port (/dev/ttyAMA0),
    which is the standard setup when running scripts directly on the
    Pi inside the robot.

Line assumption:
    Dark line (e.g. black tape) on a lighter floor. Flip DARK_LINE to
    False if you're using a light line on a dark floor instead.

Install:
    pip3 install opencv-python numpy xgo-pythonlib
    (or xgo-toolkit, depending on which fork your firmware uses)

Run:
    python3 line_follower.py
    Ctrl+C to stop.
"""

import time
import cv2
import numpy as np
from xgolib import XGO

# ---------------------------------------------------------------------
# Hardware setup
# ---------------------------------------------------------------------
dog = XGO(port='/dev/ttyAMA0', version="xgolite")

# ---------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------
DARK_LINE = True          # True: dark line on light floor. False: reverse.
THRESH_VALUE = 40          # brightness cutoff for line segmentation (0-255)
ROI_HEIGHT_FRAC = 0.30     # bottom fraction of the frame to scan for the line
MIN_LINE_AREA = 500        # ignore tiny noise blobs (pixels)

FORWARD_STEP = 12          # forward speed, xgolib 'x' range is [-25, 25]
MAX_TURN_SPEED = 45        # cap on turn speed, xgolib range is [-150, 150]
KP = 0.35                  # proportional gain: turn_speed = KP * error_px_normalized

LOST_LINE_TIMEOUT = 1.0    # seconds without a line before stopping/searching
SEARCH_TURN_SPEED = 25     # slow spin speed used to reacquire a lost line


def get_line_center(frame):
    """Returns (cx, roi_frame, mask) where cx is the line's x-centroid
    in the ROI, or None if no line is found."""
    h, w = frame.shape[:2]
    roi_top = int(h * (1 - ROI_HEIGHT_FRAC))
    roi = frame[roi_top:h, :]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    if DARK_LINE:
        _, mask = cv2.threshold(gray, THRESH_VALUE, 255, cv2.THRESH_BINARY_INV)
    else:
        _, mask = cv2.threshold(gray, THRESH_VALUE, 255, cv2.THRESH_BINARY)

    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, roi, mask

    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < MIN_LINE_AREA:
        return None, roi, mask

    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None, roi, mask

    cx = int(M["m10"] / M["m00"])
    return cx, roi, mask


def main():
    dog.pace("slow")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open camera.")
        return

    last_seen_time = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Frame grab failed.")
                break

            h, w = frame.shape[:2]
            frame_center = w // 2

            cx, roi, mask = get_line_center(frame)

            if cx is not None:
                last_seen_time = time.time()

                # Normalize error to roughly [-1, 1]
                error = (cx - frame_center) / frame_center
                turn_speed = -KP * error * MAX_TURN_SPEED
                turn_speed = max(-MAX_TURN_SPEED, min(MAX_TURN_SPEED, turn_speed))

                if(error > 0.2):
                    print("turn right\n")
                    dog.turn(-20)
                elif(error < -0.2):
                    print("turn left\n")
                    dog.turn(20)
                else:
                    print("move forward\n")
                    dog.move('x', 25)

                cv2.circle(roi, (cx, roi.shape[0] // 2), 6, (0, 255, 0), -1)
                cv2.putText(frame, f"error={error:+.2f} turn={turn_speed:+.1f}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (0, 255, 0), 2)
            else:
                dog.stop()
                # Line lost — stop briefly, then spin slowly to search
                # elapsed = time.time() - last_seen_time
                # if elapsed < LOST_LINE_TIMEOUT:
                #     dog.stop()
                # else:
                #     dog.turn(SEARCH_TURN_SPEED)
                cv2.putText(frame, "LINE LOST - searching", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            cv2.imshow("Camera", frame)
            cv2.imshow("Mask", mask)

            time.sleep(0.1)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        pass
    finally:
        dog.stop()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
