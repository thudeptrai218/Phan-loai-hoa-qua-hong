import os
from pathlib import Path

from roboflow import Roboflow


WORKSPACE = os.getenv("ROBOFLOW_WORKSPACE", "doans-workspace-wbujt")
PROJECT = os.getenv("ROBOFLOW_PROJECT", "traicay-bcj03")
VERSION = int(os.getenv("ROBOFLOW_VERSION", "1"))
FORMAT = os.getenv("ROBOFLOW_FORMAT", "yolov8")
DATASET_DIR = Path(os.getenv("ROBOFLOW_DATASET_DIR", "Dataset_roboflow"))


def main():
    api_key = os.getenv("ROBOFLOW_API_KEY")
    if not api_key:
        raise SystemExit(
            "Thieu ROBOFLOW_API_KEY. Hay tao API key tren Roboflow va set bien moi truong ROBOFLOW_API_KEY."
        )

    rf = Roboflow(api_key=api_key)
    project = rf.workspace(WORKSPACE).project(PROJECT)
    dataset = project.version(VERSION).download(FORMAT)

    data_yaml = Path(dataset.location) / "data.yaml"
    if not data_yaml.exists():
        matches = list(Path(dataset.location).rglob("data.yaml"))
        if not matches:
            raise SystemExit(f"Khong tim thay data.yaml sau khi tai dataset: {dataset.location}")
        data_yaml = matches[0]

    print(f"Da tai dataset Roboflow ve: {dataset.location}")
    print(f"File train data: {data_yaml}")
    print("Tiep theo chay: python train_model.py")


if __name__ == "__main__":
    main()
