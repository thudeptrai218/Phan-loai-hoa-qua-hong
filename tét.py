from pathlib import Path
import os

import cv2
from ultralytics import YOLO


DROIDCAM_IP = os.getenv("DROIDCAM_IP", "192.168.100.114")
DROIDCAM_PORT = os.getenv("DROIDCAM_PORT", "4747")
DROIDCAM_URL = os.getenv("DROIDCAM_URL", f"http://{DROIDCAM_IP}:{DROIDCAM_PORT}/video")
ALLOW_CAMERA_FALLBACK = os.getenv("ALLOW_CAMERA_FALLBACK", "0") == "1"
FALLBACK_CAMERA_INDEX = int(os.getenv("FALLBACK_CAMERA_INDEX", "0"))

MODEL_PATH = "runs/detect/rotten_fruit/weights/best.pt"
CONFIDENCE_THRESHOLD = 0.75

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

if not Path(MODEL_PATH).exists():
    raise FileNotFoundError(
        f"Khong tim thay model moi: {MODEL_PATH}. Hay train Roboflow truoc khi chay."
    )

model = YOLO(MODEL_PATH)


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


def get_class_name(class_id):
    return CLASS_NAMES.get(class_id, f"Lop {class_id}")


def is_defective(class_id):
    return class_id in DEFECTIVE_CLASS_IDS


def get_status(class_id):
    return DEFECTIVE_STATUS if is_defective(class_id) else FRESH_STATUS


cap = open_camera()
if cap is None:
    print("Khong the ket noi den DroidCam!")
    print("Da thu cac nguon:")
    for source in get_camera_sources():
        print(f"- {source}")
    raise SystemExit(1)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Loi khi nhan du lieu tu camera!")
        break

    results = model(frame)

    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        confidence = float(box.conf[0])
        class_id = int(box.cls[0])

        if confidence < CONFIDENCE_THRESHOLD:
            continue
        if class_id not in CLASS_NAMES:
            continue

        class_name = get_class_name(class_id)
        defective = is_defective(class_id)
        status = get_status(class_id)

        color = (0, 0, 255) if defective else (0, 180, 0)
        label = f"{class_name} - {status} {confidence:.2f}"

        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.putText(
            frame,
            label,
            (int(x1), max(int(y1) - 10, 24)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
        )

    cv2.imshow("DroidCam - Fresh/Rotten Fruit Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
