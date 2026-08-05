# XGO Lite Workshop

A hands-on workshop where you program a quadruped robot dog using Python. The robot runs a Raspberry Pi, so you can connect to it over the network and run scripts directly on the hardware.

---

## Connecting to the Robot

Before you can connect to the robot you need to make sure it's on the same network as your laptop.
To do so you need to add the SSID and password of your wifi network to the robot.
This can be done by having it's camera scan the QR code on your mobile phone by sharing the network you want the robot to connect to.
https://docs.google.com/document/d/15MvHfDQDW5mT1O_XRLc6QtZqjjpieBM6wqgk4J_BnBg/edit?tab=t.0#heading=h.cjzhwvmojcsd
### Default credentials

| Field    | Value |
|----------|-------|
| Username | `pi`  |
| Password | `pi`  |


---

### SSH (terminal access)

SSH gives you a command-line shell on the robot's Raspberry Pi.

To copy a script from your laptop to the robot:
```bash
scp scripts/robo-walk.py pi@<input.robot.ip.here>:/home/pi/
```

To run it on the robot:
```bash
ssh pi@192.168.4.1 "python /home/pi/robo-walk.py"
```

---

### VNC (graphical desktop)

VNC lets you see and control the robot's desktop remotely — useful when working with the camera feed or OpenCV windows.

1. Download **TigerVNC** (free): https://github.com/TigerVNC/tigervnc/releases
2. Open TigerVNC and enter the robot's IP address.
3. Log in with the credentials above.

The desktop that appears is running directly on the robot's Raspberry Pi.

---

## Running Scripts

All scripts must run **on the robot** (not on your laptop), because the serial port `/dev/ttyAMA0` and the camera are physically connected to the Pi inside the robot.

1. SSH into the robot.
2. Navigate to the scripts folder or copy your script there.
3. Run with `python <script_name>.py`.

Install dependencies if needed:
```bash
pip3 install xgolib opencv-python numpy
```

---

## Assignments

Work directly on the robot via SSH or VNC.

---

### Assignment 1 — Connecting to robot (15 min)

**Goal:** Connect robot to the correct WIFI network and access through SSH of VNC

**Your task:**

- Make sure your laptop and phone are connected to the correct WIFI network
- Create a QR code on your phone
- Scan the QR code with the camera of the robot
  - On the robot use the buttons on the sides of the screen to navigate to "Try Demo"
  - Browse through the multiple options and select "Network"
  - The robot will start the camera, hold the QR code from your phone in front of the camera and wait for you to scan it
  - The robot will then connect to your wifi network and you can access the robot via SSH or VNC
  - Reboot the robot
- In the main menu of the robot, select "Program"
- A IP address will be displayed on the robot's screen. This IP can be used to connect to the robot.
- Connect to the robot via SSH or VNC


### Assignment 2 — git push -u origin main (30 min)

**Goal:** Make the robot perform a set of actions.

**Your task:**
- Use SSH or VNC to connect to the robot
- Look at the exampel scripts in the `scripts` folder
- Study the code and write your own script to make the robot move

**Useful API calls:**

```python
dog.move('x', 18)          # forward (positive) or backward (negative), mm
dog.move('y', 10)          # strafe left/right
dog.turn(60)               # turn at degrees/second (negative = right)
dog.attitude(['p', 'y', 'r'], [pitch, yaw, roll])  # body tilt in degrees
dog.pace('normal')         # gait: 'slow', 'normal', 'high'
dog.stop()                 # stop all movement
dog.read_battery()         # returns battery % as an integer
```

**Done when:** The robot completes your sequence of actions.

---

### Assignment 3 — Look at the ball (30 min)

**Goal:** Use the camera to make the dog react to the ball.

The robot has a front-facing camera that can be used to detect objects in the environment.

**Your task:**

Look at the example script `scripts/detect_ball.py` and study the code.
This code reads the camera feed, creates a mask image and uses OpenCV to find the ball in the image.
It highlights the ball, including the coordinates, size and distance to the camera and displays it on the screen.

If you are connected to the robot via VNC, it will also open windows to show the camera feed and the mask image.
Write a script that makes the robot react to the ball.

**Done when:** The robot performs at least one action when the ball is in the camera's view.

---


### Assignment 4 — Fetch! (30 min)

**Goal:** Combine the last two assignments and make the robot detect a ball, pick it up and bring it to a highlighted area.

In the last two assignments you made the robot move and used the camera to detect objects.
In this assignment you will combine the two to make the robot interact with the ball and the environment.

**Your task:**

Use your previous scripts to make the robot detect the ball and pick it up.
If you were unable to do this in the previous assignments, use the `grab_object.py` script in the `scripts` folder.

Pick up the ball and bring it to a highlighted area using the actions from the previous assignments.

**Done when:** The robot performs at least one action when the ball is in the camera's view.

---

Useful links:
- https://docs.google.com/document/d/15MvHfDQDW5mT1O_XRLc6QtZqjjpieBM6wqgk4J_BnBg/edit?tab=t.0#heading=h.cjzhwvmojcsd
- https://wiki.elecfreaks.com/en/pico/cm4-xgo-robot-kit/advanced-development/python-development
- https://raspberrytips.com/remote-desktop-raspberry-pi/#2-ssh-with-x11-forwarding