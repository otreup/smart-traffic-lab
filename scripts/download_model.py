from __future__ import annotations

import argparse
import os
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
config_dir = project_root / "logs" / "ultralytics"
config_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("YOLO_CONFIG_DIR", str(config_dir))

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser(description="Descarga o valida un modelo YOLO base.")
    parser.add_argument("--model", default="yolo11n.pt", help="Modelo base de Ultralytics.")
    args = parser.parse_args()

    model = YOLO(args.model)
    output = Path(args.model)
    print(f"Modelo listo: {model.model_name if hasattr(model, 'model_name') else args.model}")
    if output.exists():
        print(f"Archivo local: {output.resolve()}")
    else:
        print("Ultralytics cargo el modelo, pero no lo dejo en la carpeta del proyecto.")


if __name__ == "__main__":
    main()
