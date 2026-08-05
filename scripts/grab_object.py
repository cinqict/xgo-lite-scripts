"""
Basic Grab Routine for XGO Lite Arm
--------------------------------------
Uses xgolib's arm(x, z) and claw(pos) functions to pick up an object
in front of the robot.

Coordinate system:
    arm_x: forward/back reach, relative to arm base, range [-80, 155] mm
    arm_z: up/down reach, relative to arm base, range [-95, 155] mm
    claw:  0 = fully open, 255 = fully closed

You'll need to tune the X/Z values below to match where your object
actually is relative to the arm base — these are just reasonable
starting points, not universal values.
"""

import time
from xgolib import XGO

dog = XGO(port='/dev/ttyAMA0', version="xgolite")

# ---------------------------------------------------------------------
# Tune these positions for your object's actual location
# ---------------------------------------------------------------------
HOVER_X, HOVER_Z = 100, 40     # position above/near the object, claw open
GRAB_X, GRAB_Z = 130, -60      # lowered down to actually grip the object
LIFT_X, LIFT_Z = 80, 100       # raised back up after grabbing

CLAW_OPEN = 60
CLAW_CLOSED = 220

MOVE_SETTLE_TIME = 1.0          # seconds to let the arm reach position


def grab_object():
    print("Lowering body...")
    dog.attitude('p', 15)

    print("Opening claw...")
    dog.claw(CLAW_OPEN)
    time.sleep(0.5)

    print("Moving arm to hover position...")
    dog.arm(HOVER_X, HOVER_Z)
    time.sleep(MOVE_SETTLE_TIME)

    print("Lowering to grab position...")
    dog.arm(GRAB_X, GRAB_Z)
    time.sleep(MOVE_SETTLE_TIME)

    print("Closing claw...")
    dog.claw(CLAW_CLOSED)
    time.sleep(0.8)

    print("Lifting object...")
    dog.arm(LIFT_X, LIFT_Z)
    time.sleep(MOVE_SETTLE_TIME)

    print("Standing up...")
    dog.attitude('p', 0)

    print("Done.")


def release_object():
    print("Opening claw to release...")
    dog.claw(CLAW_OPEN)
    time.sleep(0.5)


if __name__ == "__main__":
    grab_object()
    time.sleep(2)
    # release_object()   # uncomment to drop it again
