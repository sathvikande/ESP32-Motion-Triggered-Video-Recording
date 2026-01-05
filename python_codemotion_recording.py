import cv2
import os
import time
import requests

# ===========================
# ESP32 SETTINGS
# ===========================
ESP32_IP = "172.16.0.6"        # 🔁 Change if needed
MOTION_URL = f"http://{ESP32_IP}/motion"

# ===========================
# CAMERA SETTINGS
# ===========================
CAMERA_URL = "http://172.16.0.5:4747/video"

SAVE_FOLDER = "recordings"
os.makedirs(SAVE_FOLDER, exist_ok=True)

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# ===========================
# OPEN CAMERA
# ===========================
print("Connecting to camera...")
camera = cv2.VideoCapture(CAMERA_URL, cv2.CAP_FFMPEG)
time.sleep(2)

if not camera.isOpened():
    print("❌ Camera not available")
    exit()

# 🔴 AUTO FPS FIX (IMPORTANT)
FPS = camera.get(cv2.CAP_PROP_FPS)
if FPS == 0 or FPS > 60:
    FPS = 10.0   # Safe fallback for IP cameras

print("✅ Camera connected")
print("🎥 Recording FPS:", FPS)
print("📡 Waiting for ESP32 PIR trigger...\n")

# ===========================
# VARIABLES
# ===========================
recording = False
out = None
last_state = "0"

# ===========================
# MAIN LOOP
# ===========================
while True:

    # ---------------------------
    # READ PIR STATE FROM ESP32
    # ---------------------------
    try:
        response = requests.get(MOTION_URL, timeout=0.5)
        pir_state = response.text.strip()
    except:
        pir_state = "0"

    # ---------------------------
    # READ CAMERA FRAME
    # ---------------------------
    ret, frame = camera.read()
    if not ret:
        continue

    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

    # ---------------------------
    # START RECORDING
    # ---------------------------
    if pir_state == "1" and not recording:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        video_path = os.path.join(
            SAVE_FOLDER, f"motion_{timestamp}.mp4"
        )

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(
            video_path, fourcc, FPS,
            (FRAME_WIDTH, FRAME_HEIGHT)
        )

        print("🔴 Recording started:", video_path)
        recording = True

    # ---------------------------
    # RECORD FRAME
    # ---------------------------
    if recording:
        out.write(frame)

        if pir_state == "0":
            print("⏹ Recording stopped")
            recording = False
            out.release()

    # ---------------------------
    # DISPLAY LIVE FEED
    # ---------------------------
    cv2.imshow("Live Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ===========================
# CLEANUP
# ===========================
camera.release()
if out:
    out.release()
cv2.destroyAllWindows()