from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.esp32_yolo.camera import CameraClient
from src.esp32_yolo.detector import YOLODetector
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
    detector = YOLODetector(settings.preferred_model(), settings.confidence, settings.iou, settings.image_size)
    capture = camera.open()
    raw_dir = Path(settings.capture.output_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    print("Deteccion en vivo iniciada. Teclas: q=salir, s=guardar frame.")
    try:
        while True:
            ok, frame = capture.read()
            if not ok or frame is None:
                print("No llego frame de la ESP32-CAM.")
                continue

            detections = detector.detect(frame)
            annotated = detector.draw(frame, detections)
            cv2.imshow("ESP32-CAM YOLO", annotated)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("s"):
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                path = raw_dir / f"manual_{stamp}.jpg"
                cv2.imwrite(str(path), frame)
                print(f"Frame guardado: {path}")
    finally:
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
