"""
WASD Teleop for XGO Lite
--------------------------
Drive the robot dog with the keyboard, works fine over SSH (no GUI
needed) since it reads keys directly in the terminal via curses.

Controls:
    w / s   - forward / backward
    a / d   - turn left / turn right
    space   - stop immediately
    +/-     - increase / decrease speed
    q       - quit (also stops the dog)

Behavior notes:
    Terminal input has no "key released" event — only "key pressed."
    So this uses a watchdog: the dog keeps moving as long as keys keep
    arriving (held keys auto-repeat in most terminals), and it auto-stops
    if no key has arrived for STOP_TIMEOUT seconds. This means letting go
    of a key stops the dog shortly afterward, and losing your SSH
    connection doesn't leave it walking forever.

Install:
    pip3 install xgo-pythonlib   # or xgo-toolkit, whichever matches your firmware

Run:
    python3 wasd_teleop.py
"""

import curses
import time
from xgolib import XGO

# ---------------------------------------------------------------------
# Hardware setup
# ---------------------------------------------------------------------
dog = XGO(port='/dev/ttyAMA0', version="xgolite")

# ---------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------
FORWARD_STEP_DEFAULT = 15    # xgolib 'x' move range is [-25, 25]
TURN_SPEED_DEFAULT = 50      # xgolib turn range is [-150, 150]
STEP_INCREMENT = 5

STOP_TIMEOUT = 0.3           # seconds of no keypress before auto-stopping
LOOP_DELAY = 0.02            # seconds between input polls


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def main(stdscr):
    curses.curs_set(0)         # hide cursor
    stdscr.nodelay(True)       # non-blocking getch()
    stdscr.timeout(0)

    forward_step = FORWARD_STEP_DEFAULT
    turn_speed = TURN_SPEED_DEFAULT

    last_key_time = time.time()
    current_action = None      # 'forward' | 'backward' | 'left' | 'right' | None
    stopped = True

    stdscr.addstr(0, 0, "XGO WASD Teleop -- w/a/s/d to move, space to stop, "
                        "+/- speed, q to quit")

    try:
        while True:
            key = stdscr.getch()

            if key != -1:
                last_key_time = time.time()

                if key in (ord('q'), ord('Q')):
                    break
                elif key in (ord('w'), ord('W')):
                    current_action = 'forward'
                elif key in (ord('s'), ord('S')):
                    current_action = 'backward'
                elif key in (ord('a'), ord('A')):
                    current_action = 'left'
                elif key in (ord('d'), ord('D')):
                    current_action = 'right'
                elif key == ord(' '):
                    current_action = None
                    dog.stop()
                    stopped = True
                elif key in (ord('+'), ord('=')):
                    forward_step = clamp(forward_step + STEP_INCREMENT, 0, 25)
                    turn_speed = clamp(turn_speed + STEP_INCREMENT * 3, 0, 150)
                elif key in (ord('-'), ord('_')):
                    forward_step = clamp(forward_step - STEP_INCREMENT, 0, 25)
                    turn_speed = clamp(turn_speed - STEP_INCREMENT * 3, 0, 150)

            idle_time = time.time() - last_key_time

            if idle_time > STOP_TIMEOUT:
                if not stopped:
                    dog.stop()
                    stopped = True
                current_action = None
            elif current_action is not None:
                stopped = False
                if current_action == 'forward':
                    dog.move('x', forward_step)
                elif current_action == 'backward':
                    dog.move('x', -forward_step)
                elif current_action == 'left':
                    dog.turn(turn_speed)
                elif current_action == 'right':
                    dog.turn(-turn_speed)

            stdscr.addstr(2, 0, f"action: {current_action or 'stopped':<10}  "
                                f"speed(step/turn): {forward_step}/{turn_speed}   ")
            stdscr.clrtoeol()
            stdscr.refresh()

            time.sleep(LOOP_DELAY)

    finally:
        dog.stop()


if __name__ == "__main__":
    curses.wrapper(main)