"""
Ping Pong Ball Detector for XGO Lite
--------------------------------------
Detects a ping pong ball using color segmentation (HSV) + circularity
filtering, and estimates distance from the ball's apparent size.

Usage:
    python3 detect_ping_pong_ball.py

Controls:
    q - quit
    c - cycle through color presets (orange / white)

Notes:
- Tune HSV ranges below for your lighting conditions. Cheap indoor
  lighting can shift white/orange balls quite a bit, so this is the
  #1 thing you'll want to adjust.
- Uses cv2.VideoCapture(0) which works for both USB webcams and most
  Pi camera setups (with libcamera's V4L2 compatibility layer enabled).
  If that fails on your Pi, see the picamera2 fallback notes at the
  bottom of this file.
"""

import cv2
import numpy as np

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

# Real-world ping pong ball diameter in mm (for distance estimate)
BALL_DIAMETER_MM = 20.0

# Approximate focal length in pixels — calibrate this for your camera
# by measuring a known distance/pixel-radius pair and solving:
#   FOCAL_LENGTH_PX = (pixel_radius * known_distance_mm) / (BALL_DIAMETER_MM / 2)
FOCAL_LENGTH_PX = 600.0

MIN_RADIUS_PX = 6         # ignore tiny noise blobs
MIN_CIRCULARITY = 0.7     # 1.0 = perfect circle, contours rate lower


def detect_ball(frame, color_name):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    preset = COLOR_PRESETS[color_name]
    mask = cv2.inRange(hsv, preset["lower"], preset["upper"])

    # Clean up the mask
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

        # Prefer larger, more circular candidates
        score = circularity * area
        if score > best_score:
            best_score = score
            best = (int(x), int(y), int(radius))

    return best, mask


def estimate_distance_mm(radius_px):
    if radius_px <= 0:
        return None
    return (BALL_DIAMETER_MM / 2) * FOCAL_LENGTH_PX / radius_px


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open camera. See picamera2 fallback notes "
              "at the bottom of this script.")
        return

    color_names = list(COLOR_PRESETS.keys())
    color_idx = 0

    print("Press 'c' to switch color preset, 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame grab failed.")
            break

        color_name = color_names[color_idx]
        result, mask = detect_ball(frame, color_name)

        if result:
            x, y, r = result
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
            cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)

            dist = estimate_distance_mm(r)
            label = f"{color_name} ball  r={r}px"
            if dist:
                label += f"  ~{dist/10:.1f}cm"
            cv2.putText(frame, label, (x - 40, y - r - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # This (x, y, r) is what you'd feed into XGO movement logic,
            # e.g. turn toward ball if x is off-center, move forward
            # until estimated distance is small enough.
        else:
            cv2.putText(frame, f"Searching ({color_name})...", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.imshow("XGO Ball Detection", frame)
        cv2.imshow("Mask", mask)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            color_idx = (color_idx + 1) % len(color_names)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

# ---------------------------------------------------------------------
# picamera2 fallback (if cv2.VideoCapture(0) doesn't find your camera):
#
# from picamera2 import Picamera2
# picam2 = Picamera2()
# picam2.configure(picam2.create_preview_configuration(
#     main={"format": "RGB888", "size": (640, 480)}))
# picam2.start()
# while True:
#     frame = picam2.capture_array()
#     ... (rest is identical to the loop above, minus cap.read())
# ---------------------------------------------------------------------
