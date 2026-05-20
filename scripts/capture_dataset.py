from __future__ import annotations

from datetime import datetime
from pathlib import Path
import argparse
import sys
import time

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.esp32_yolo.camera import CameraClient
from src.esp32_yolo.settings import load_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Captura imagenes desde la ESP32-CAM para crear dataset YOLO.")
    parser.add_argument("--seconds", type=float, default=60.0, help="Duracion total de captura.")
    parser.add_argument("--every", type=float, default=1.0, help="Intervalo entre imagenes.")
    parser.add_argument("--output", type=Path, default=None, help="Carpeta de salida.")
    args = parser.parse_args()

    settings = load_settings()
    output_dir = args.output or Path(settings.capture.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    camera = CameraClient(
        settings.camera_url,
        settings.fallback_camera_url,
        urls=settings.camera_urls,
        snapshot_urls=settings.snapshot_urls,
        source=settings.camera_source,
        webcam_index=settings.webcam_index,
        use_webcam_fallback=settings.use_webcam_fallback,
    )
    capture = camera.open()
    start = time.monotonic()
    next_capture = start
    saved = 0

    try:
        while time.monotonic() - start < args.seconds:
            ok, frame = capture.read()
            if not ok or frame is None:
                print("Frame perdido, intentando de nuevo...")
                time.sleep(0.2)
                continue

            cv2.imshow("Recolector ESP32-CAM", frame)
            now = time.monotonic()
            if now >= next_capture:
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                path = output_dir / f"{settings.capture.prefix}_{stamp}.jpg"
                cv2.imwrite(str(path), frame)
                saved += 1
                print(f"Guardada: {path}")
                next_capture = now + args.every

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()

    print(f"Captura terminada. Imagenes guardadas: {saved}")


if __name__ == "__main__":
    main()
