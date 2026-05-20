from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
config_dir = project_root / "logs" / "ultralytics"
config_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("YOLO_CONFIG_DIR", str(config_dir))

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrena YOLO para detectar carros de juguete.")
    parser.add_argument("--data", default="configs/toy_car_dataset.yaml", help="Archivo YAML del dataset.")
    parser.add_argument("--model", default="yolo11n.pt", help="Modelo base o checkpoint.")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default=None, help="Usa 0 para GPU NVIDIA, cpu para procesador.")
    args = parser.parse_args()

    if not Path(args.data).exists():
        raise FileNotFoundError(f"No existe el dataset YAML: {args.data}")

    model = YOLO(args.model)
    train_args = {
        "data": args.data,
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "name": "toy_car_detector",
        "project": "runs/detect",
        "patience": 20,
    }
    if args.device is not None:
        train_args["device"] = args.device

    model.train(**train_args)


if __name__ == "__main__":
    main()
