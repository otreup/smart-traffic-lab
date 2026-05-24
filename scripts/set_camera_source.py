from __future__ import annotations

import argparse
from pathlib import Path

import yaml


VALID_SOURCES = {"auto", "esp32", "webcam"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Cambia la fuente de camara del proyecto.")
    parser.add_argument("source", choices=sorted(VALID_SOURCES), help="auto, esp32 o webcam")
    parser.add_argument("--webcam-index", type=int, default=None, help="Indice de webcam, normalmente 0.")
    args = parser.parse_args()

    settings_path = Path("configs/settings.yaml")
    data = yaml.safe_load(settings_path.read_text(encoding="utf-8")) or {}
    data["camera_source"] = args.source
    data["use_webcam_fallback"] = args.source in {"auto", "webcam"}
    if args.webcam_index is not None:
        data["webcam_index"] = args.webcam_index

    settings_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"Camara configurada en modo: {args.source}")
    if args.source == "auto":
        print("Primero intenta ESP32-CAM y si falla usa webcam.")
    elif args.source == "esp32":
        print("Solo usara la ESP32-CAM.")
    else:
        print(f"Solo usara la webcam indice {data.get('webcam_index', 0)}.")


if __name__ == "__main__":
    main()
