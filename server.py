from pathlib import Path
import os
import queue
import threading
import time

import cv2
import numpy as np
import requests
from flask import Flask, Response, jsonify, render_template
from ultralytics import YOLO


DROIDCAM_IP = os.getenv("DROIDCAM_IP", "172.20.10.3")
DROIDCAM_PORT = os.getenv("DROIDCAM_PORT", "4747")
DROIDCAM_URL = os.getenv("DROIDCAM_URL", f"http://{DROIDCAM_IP}:{DROIDCAM_PORT}/video")
ALLOW_CAMERA_FALLBACK = os.getenv("ALLOW_CAMERA_FALLBACK", "0") == "1"
FALLBACK_CAMERA_INDEX = int(os.getenv("FALLBACK_CAMERA_INDEX", "0"))
ESP8266_IP = os.getenv("ESP8266_IP", "192.168.4.1")
ESP8266_URL = os.getenv("ESP8266_URL", f"http://{ESP8266_IP}/control")
AUTO_DISCOVER_ESP8266 = os.getenv("AUTO_DISCOVER_ESP8266", "1") == "1"
ENABLE_HARDWARE = os.getenv("ENABLE_HARDWARE", "1") == "1"

MODEL_PATH = "runs/detect/rotten_fruit/weights/best.pt"
CONFIDENCE_THRESHOLD = 0.7
HISTORY_COOLDOWN_SECONDS = 1.5
SERVO_COOLDOWN_SECONDS = float(os.getenv("SERVO_COOLDOWN_SECONDS", "2.0"))
SERVO_FAIL_COOLDOWN_SECONDS = float(os.getenv("SERVO_FAIL_COOLDOWN_SECONDS", "8.0"))
SERVO_STABLE_FRAMES = int(os.getenv("SERVO_STABLE_FRAMES", "3"))
ESP8266_TIMEOUT_SECONDS = float(os.getenv("ESP8266_TIMEOUT_SECONDS", "0.35"))
ESP8266_DISCOVERY_TIMEOUT_SECONDS = float(os.getenv("ESP8266_DISCOVERY_TIMEOUT_SECONDS", "0.12"))
MAX_HISTORY_ITEMS = 80

# Roboflow label order for the new dataset:
# 0: Qua Hong
# 1: Qua Tuoi
CLASS_NAMES = {
    0: "Qua hong",
    1: "Qua tuoi",
}
DEFECTIVE_CLASS_IDS = {0}
FRESH_STATUS = "Tuoi"
DEFECTIVE_STATUS = "Hong"
ALLOWED_CLASS_IDS = set(CLASS_NAMES)
SERVO_BY_CLASS_ID = {
    0: 1,  # Qua hong -> servo 1
    1: 2,  # Qua tuoi -> servo 2
}

MIN_WIDTH = 30
MIN_HEIGHT = 30
MAX_WIDTH = 500
MAX_HEIGHT = 500

if not Path(MODEL_PATH).exists():
    raise FileNotFoundError(
        f"Khong tim thay model moi: {MODEL_PATH}. Hay train Roboflow truoc khi chay server."
    )

model = YOLO(MODEL_PATH)
app = Flask(__name__)

history = []
last_history_at = 0
last_servo_at = {}
last_servo_error_at = 0
last_candidate_class_id = None
stable_candidate_frames = 0
servo_queue = queue.Queue(maxsize=1)
hardware_status = {
    "enabled": ENABLE_HARDWARE,
    "url": ESP8266_URL,
    "discovered": False,
    "last_command": None,
    "last_ok": None,
    "last_response": None,
    "last_error_time": None,
    "last_error": None,
    "cooldown_remaining": 0,
    "pending_commands": 0,
}
hardware_worker_started = False


def get_camera_sources():
    base_url = f"http://{DROIDCAM_IP}:{DROIDCAM_PORT}"
    sources = [
        DROIDCAM_URL,
        f"{base_url}/video",
        f"{base_url}/mjpegfeed",
        f"{base_url}/videofeed",
    ]

    unique_sources = []
    for source in sources:
        if source not in unique_sources:
            unique_sources.append(source)
    return unique_sources


def make_status_frame(message, detail=""):
    frame = np.zeros((540, 960, 3), dtype=np.uint8)
    frame[:] = (24, 28, 24)
    cv2.putText(frame, message, (40, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (70, 220, 255), 2)
    if detail:
        cv2.putText(frame, detail, (40, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 220, 220), 2)
    cv2.putText(
        frame,
        "Mo DroidCam tren dien thoai va dam bao cung Wi-Fi voi may tinh.",
        (40, 320),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (180, 220, 180),
        2,
    )
    return frame


def get_class_name(class_id):
    return CLASS_NAMES.get(class_id, f"Lop {class_id}")


def is_defective(class_id):
    return class_id in DEFECTIVE_CLASS_IDS


def get_status(class_id):
    return DEFECTIVE_STATUS if is_defective(class_id) else FRESH_STATUS


def is_allowed_detection(class_id):
    return class_id in ALLOWED_CLASS_IDS


def add_history_item(class_name, status):
    global last_history_at

    now = time.time()
    if now - last_history_at < HISTORY_COOLDOWN_SECONDS:
        return

    history.append(
        {
            "time": time.strftime("%H:%M:%S"),
            "fruit": class_name,
            "status": status,
        }
    )
    del history[:-MAX_HISTORY_ITEMS]
    last_history_at = now


def get_discovery_subnets():
    subnets = []
    for ip in [DROIDCAM_IP, ESP8266_IP]:
        parts = ip.split(".")
        if len(parts) == 4:
            subnet = ".".join(parts[:3])
            if subnet not in subnets:
                subnets.append(subnet)

    for subnet in ["192.168.100", "192.168.1", "192.168.0", "192.168.4"]:
        if subnet not in subnets:
            subnets.append(subnet)
    return subnets


def ping_esp8266(base_url, timeout):
    try:
        response = requests.get(f"{base_url}/ping", timeout=timeout)
        if response.ok and "ESP8266 OK" in response.text:
            return True, response.text
    except requests.RequestException:
        pass
    return False, None


def discover_esp8266():
    global ESP8266_URL

    if not AUTO_DISCOVER_ESP8266:
        return

    current_base = ESP8266_URL.rsplit("/control", 1)[0]
    candidates = [current_base, "http://192.168.4.1"]

    for subnet in get_discovery_subnets():
        for host in [1, 2, 3, 4, 5, 6, 10, 20, 25, 50, 100, 101, 102, 103, 104, 105, 110, 114, 150, 200, 254]:
            candidates.append(f"http://{subnet}.{host}")

    seen = set()
    for base_url in candidates:
        if base_url in seen:
            continue
        seen.add(base_url)

        ok, text = ping_esp8266(base_url, ESP8266_DISCOVERY_TIMEOUT_SECONDS)
        if ok:
            ESP8266_URL = f"{base_url}/control"
            hardware_status["url"] = ESP8266_URL
            hardware_status["discovered"] = True
            hardware_status["last_response"] = text
            hardware_status["last_error"] = None
            print(f"Da tu tim thay ESP8266: {ESP8266_URL}")
            return


def send_servo_command(class_id):
    global last_servo_error_at

    if not ENABLE_HARDWARE:
        return

    discover_esp8266()

    servo = SERVO_BY_CLASS_ID.get(class_id)
    if servo is None:
        return

    now = time.time()
    if now - last_servo_at.get(servo, 0) < SERVO_COOLDOWN_SECONDS:
        return
    if now - last_servo_error_at < SERVO_FAIL_COOLDOWN_SECONDS:
        return

    # Cool down on attempt, not only on success, so a disconnected ESP8266 cannot spam requests.
    last_servo_at[servo] = now
    hardware_status["last_command"] = {
        "time": time.strftime("%H:%M:%S"),
        "servo": servo,
        "class_id": class_id,
        "class_name": get_class_name(class_id),
        "status": get_status(class_id),
    }

    try:
        response = requests.get(f"{ESP8266_URL}?servo={servo}", timeout=ESP8266_TIMEOUT_SECONDS)
        response.raise_for_status()
        hardware_status["last_ok"] = time.strftime("%H:%M:%S")
        hardware_status["last_response"] = response.text
        hardware_status["last_error"] = None
        hardware_status["last_error_time"] = None
        print(f"Da gui lenh servo {servo} cho class {class_id}")
    except requests.RequestException as exc:
        last_servo_error_at = now
        hardware_status["last_error"] = str(exc)
        hardware_status["last_error_time"] = time.strftime("%H:%M:%S")
        print(f"Loi gui lenh den ESP8266, tam dung gui {SERVO_FAIL_COOLDOWN_SECONDS}s: {exc}")


def enqueue_servo_command(class_id):
    if not ENABLE_HARDWARE:
        return

    try:
        servo_queue.put_nowait(class_id)
    except queue.Full:
        # Keep the newest stable command and drop stale pending work.
        try:
            servo_queue.get_nowait()
        except queue.Empty:
            pass
        try:
            servo_queue.put_nowait(class_id)
        except queue.Full:
            pass


def servo_worker():
    while True:
        class_id = servo_queue.get()
        try:
            send_servo_command(class_id)
        finally:
            servo_queue.task_done()


def ensure_hardware_worker():
    global hardware_worker_started

    if hardware_worker_started or not ENABLE_HARDWARE:
        return

    thread = threading.Thread(target=servo_worker, daemon=True)
    thread.start()
    hardware_worker_started = True


def choose_detection_for_hardware(detections):
    if not detections:
        return None

    # If rotten fruit is present, prioritize removing it first. Otherwise use highest confidence.
    defective = [item for item in detections if is_defective(item["class_id"])]
    candidates = defective if defective else detections
    return max(candidates, key=lambda item: item["confidence"])


def maybe_send_stable_servo_command(detections):
    global last_candidate_class_id, stable_candidate_frames

    selected = choose_detection_for_hardware(detections)
    if selected is None:
        last_candidate_class_id = None
        stable_candidate_frames = 0
        return

    class_id = selected["class_id"]
    if class_id == last_candidate_class_id:
        stable_candidate_frames += 1
    else:
        last_candidate_class_id = class_id
        stable_candidate_frames = 1

    if stable_candidate_frames >= SERVO_STABLE_FRAMES:
        enqueue_servo_command(class_id)
        stable_candidate_frames = 0


def try_open_source(source):
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        cap.release()
        return None

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    for _ in range(12):
        ret, frame = cap.read()
        if ret and frame is not None and frame.size > 0:
            print(f"Dang dung DroidCam: {source}")
            return cap
        time.sleep(0.1)

    cap.release()
    return None


def open_camera():
    for source in get_camera_sources():
        cap = try_open_source(source)
        if cap is not None:
            return cap

    if ALLOW_CAMERA_FALLBACK:
        print("Khong mo duoc DroidCam. Thu camera may tinh...")
        cap = cv2.VideoCapture(FALLBACK_CAMERA_INDEX, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(FALLBACK_CAMERA_INDEX)
        if cap.isOpened():
            return cap

    return None


def detect_objects():
    ensure_hardware_worker()
    cap = open_camera()

    while True:
        if cap is None:
            yield make_status_frame(
                "Khong ket noi duoc DroidCam",
                f"Dang thu: {', '.join(get_camera_sources())}",
            )
            time.sleep(1)
            cap = open_camera()
            continue

        ret, frame = cap.read()
        if not ret:
            print("Loi: Khong lay duoc frame tu DroidCam/camera!")
            cap.release()
            time.sleep(1)
            cap = open_camera()
            continue

        results = model(frame)

        detections = []

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            width, height = x2 - x1, y2 - y1

            if not is_allowed_detection(class_id):
                continue
            if confidence < CONFIDENCE_THRESHOLD:
                continue
            if width < MIN_WIDTH or height < MIN_HEIGHT or width > MAX_WIDTH or height > MAX_HEIGHT:
                continue

            class_name = get_class_name(class_id)
            defective = is_defective(class_id)
            status = get_status(class_id)
            color = (0, 0, 255) if defective else (0, 180, 0)
            label = f"{class_name} - {status} ({confidence:.2f})"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 24)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

            add_history_item(class_name, status)
            detections.append(
                {
                    "class_id": class_id,
                    "confidence": confidence,
                    "status": status,
                }
            )

        maybe_send_stable_servo_command(detections)

        yield frame


def generate_frames():
    for frame in detect_objects():
        _, buffer = cv2.imencode(".jpg", frame)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )


@app.route("/")
def index():
    return render_template("web_dashboard.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/history")
def get_history():
    return jsonify(history)


@app.route("/hardware_status")
def get_hardware_status():
    if last_servo_error_at:
        remaining = SERVO_FAIL_COOLDOWN_SECONDS - (time.time() - last_servo_error_at)
        hardware_status["cooldown_remaining"] = max(0, round(remaining, 1))
    else:
        hardware_status["cooldown_remaining"] = 0
    hardware_status["pending_commands"] = servo_queue.qsize()
    return jsonify(hardware_status)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6003, debug=True)
