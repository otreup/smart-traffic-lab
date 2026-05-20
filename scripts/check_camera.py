from __future__ import annotations

import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.esp32_yolo.camera import CameraClient
from src.esp32_yolo.settings import load_settings


def main() -> None:
    settings = load_settings()
    camera = CameraClient(
        settings.camera_url,
        settings.fallback_camera_url,
        urls=settings.camera_urls,
        snapshot_urls=settings.snapshot_urls,
        source=settings.camera_source,
        webcam_index=settings.webcam_index,
        use_webcam_fallback=settings.use_webcam_fallback,
    )
    frame = camera.read_frame()
    print(f"Camara OK. Frame recibido: {frame.shape[1]}x{frame.shape[0]}")
    cv2.imshow("ESP32-CAM test", frame)
    print("Presiona cualquier tecla en la ventana para cerrar.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
