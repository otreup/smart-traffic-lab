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

    try:
        import cv2

        print("MAIN listo. Teclas: q=salir, s=guardar frame desde scripts/live_detect.py para mas funciones.")
        while True:
            ok, frame = capture.read()
            if not ok or frame is None:
                print("No se pudo leer frame de la camara.")
                continue

            detections = detector.detect(frame)
            annotated = detector.draw(frame, detections)
            cv2.imshow("ESP32-CAM YOLO", annotated)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
