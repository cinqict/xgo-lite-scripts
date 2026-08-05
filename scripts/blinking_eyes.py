"""
Blinking Eyes on XGO Lite's LCD Screen
------------------------------------------
Draws a simple pair of eyes on the built-in LCD and blinks them on a
randomized timer, using xgoedu's screen-drawing functions.

IMPORTANT: kill the robot's self-starting main.py process first, or
you'll get screen refresh conflicts:
    sudo pkill -f main.py

Screen coordinate range: x:[0,320], y:[0,240]

Install (if not already present):
    pip3 install xgo-pythonlib
"""

import time
import random
from xgoedu import XGOEDU

edu = XGOEDU()

# ---------------------------------------------------------------------
# Eye layout - tune to taste
# ---------------------------------------------------------------------
BG_COLOR = (0, 0, 0)          # screen background (black)
EYE_COLOR = (0, 200, 255)     # cyan-ish "robot eye" color
EYE_RADIUS = 35

LEFT_EYE_CENTER = (110, 120)
RIGHT_EYE_CENTER = (210, 120)

BLINK_DURATION = 0.15         # how long the eyes stay closed
MIN_OPEN_TIME = 2.0           # min time between blinks
MAX_OPEN_TIME = 5.0           # max time between blinks


def draw_filled_circle(cx, cy, radius, color):
    """lcd_circle draws an arc; a full 0-360 sweep with width == radius
    fills the whole disc, which is what we want for an 'open' eye."""
    x1, y1 = cx - radius, cy - radius
    x2, y2 = cx + radius, cy + radius
    edu.lcd_circle(x1, y1, x2, y2, 0, 360, color=color, width=radius)


def erase_eye_area(cx, cy, radius):
    """Paint over the eye's bounding box with the background color."""
    pad = 4  # small margin so we don't leave a ring behind
    edu.lcd_rectangle(cx - radius - pad, cy - radius - pad,
                      cx + radius + pad, cy + radius + pad,
                      fill=BG_COLOR, outline=BG_COLOR, width=1)


def draw_closed_eye(cx, cy, radius, color):
    """A closed eye = a thin horizontal line (eyelid)."""
    edu.lcd_line(cx - radius, cy, cx + radius, cy, color=color, width=4)


def eyes_open():
    draw_filled_circle(*LEFT_EYE_CENTER, EYE_RADIUS, EYE_COLOR)
    draw_filled_circle(*RIGHT_EYE_CENTER, EYE_RADIUS, EYE_COLOR)


def eyes_closed():
    erase_eye_area(*LEFT_EYE_CENTER, EYE_RADIUS)
    erase_eye_area(*RIGHT_EYE_CENTER, EYE_RADIUS)
    draw_closed_eye(*LEFT_EYE_CENTER, EYE_RADIUS, EYE_COLOR)
    draw_closed_eye(*RIGHT_EYE_CENTER, EYE_RADIUS, EYE_COLOR)


def blink():
    eyes_closed()
    time.sleep(BLINK_DURATION)
    erase_eye_area(*LEFT_EYE_CENTER, EYE_RADIUS)
    erase_eye_area(*RIGHT_EYE_CENTER, EYE_RADIUS)
    eyes_open()


def main():
    edu.lcd_clear()
    eyes_open()

    try:
        while True:
            wait_time = random.uniform(MIN_OPEN_TIME, MAX_OPEN_TIME)
            time.sleep(wait_time)
            blink()
    except KeyboardInterrupt:
        edu.lcd_clear()


if __name__ == "__main__":
    main()