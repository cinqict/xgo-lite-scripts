from xgolib import XGO
import time

# Initialize the robot on the default serial port
# Use 'xgolite' or 'xgomini' depending on your hardware
dog = XGO(port='/dev/ttyAMA0', version="xgolite")

# Optional: Auto-detect firmware version
version = dog.read_firmware()
if version == 'M':
    print("Detected XGO-MINI")
    dog = XGO(port='/dev/ttyAMA0', version="xgomini")
else:
    print("Detected XGO-LITE")

# --- Movement Sequence ---

# 1. Move forward 18mm
dog.move('x', 18)
time.sleep(2)

# 2. Turn left at 60 degrees/second
dog.turn(60)
time.sleep(2)

# 3. Set high pace gait
dog.pace('high')

# 4. Adjust Body Posture (Pitch: 10°, Yaw: -4°, Roll: 8°)
dog.attitude(['p', 'y', 'r'], [10, -4, 8])
time.sleep(2)

# 5. Stop all movements
dog.stop()

# 6. Check Battery Level
battery = dog.read_battery()
print(f"Battery Level: {battery}%")