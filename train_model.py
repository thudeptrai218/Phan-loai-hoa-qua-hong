import os
from pathlib import Path

from ultralytics import YOLO


def choose_data_yaml():
    candidates = [
        os.getenv("DATA_YAML"),
        "Dataset_roboflow/data.yaml",
        "traicay-1/data_train_only.yaml",
        "Dataset_rotten_clean/data.yaml",
        "Dataset/data.yaml",
    ]

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate

    raise FileNotFoundError(
        "Khong tim thay data.yaml. Hay tai dataset Roboflow bang download_roboflow_dataset.py truoc."
    )


DATA_YAML = choose_data_yaml()
BASE_MODEL = os.getenv("BASE_MODEL", "yolov8s.pt")
EPOCHS = int(os.getenv("EPOCHS", "50"))
IMGSZ = int(os.getenv("IMGSZ", "640"))
BATCH = int(os.getenv("BATCH", "16"))
RUN_NAME = os.getenv("RUN_NAME", "rotten_fruit")
PROJECT_DIR = Path("runs/detect").resolve()

print(f"Data YAML: {DATA_YAML}")
print(f"Base model: {BASE_MODEL}")

model = YOLO(BASE_MODEL)

model.train(
    data=DATA_YAML,
    epochs=EPOCHS,
    imgsz=IMGSZ,
    batch=BATCH,
    project=str(PROJECT_DIR),
    name=RUN_NAME,
    exist_ok=True,
)
