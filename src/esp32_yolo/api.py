from __future__ import annotations

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .camera import CameraClient
from .settings import load_settings
from .simulation import SimpleTrafficSimulation
from .sumo_network import parse_network, project_root
from .traffic_controller import TrafficLightController

settings = load_settings()
camera_source = settings.camera_source
camera_stream_version = 0


def build_camera(source: str | None = None) -> CameraClient:
    return CameraClient(
        settings.camera_url,
        settings.fallback_camera_url,
        urls=settings.camera_urls,
        snapshot_urls=settings.snapshot_urls,
        source=source or camera_source,
        webcam_index=settings.webcam_index,
        use_webcam_fallback=settings.use_webcam_fallback,
    )


camera = build_camera()
detector = None
controller = TrafficLightController()
simulation = SimpleTrafficSimulation()
app = FastAPI(title="Smart Traffic ESP32-CAM YOLO API", version="1.0.0")

root = project_root()
web_dir = root / "web"
app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")


def placeholder_frame(message: str = "Camara no disponible") -> np.ndarray:
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (18, 24, 28)
    cv2.putText(frame, "Smart Traffic Lab", (32, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (230, 240, 245), 2, cv2.LINE_AA)
    cv2.putText(frame, message[:48], (32, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (80, 180, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "Revisa ESP32-CAM o webcam", (32, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 190, 200), 2, cv2.LINE_AA)
    return frame


def get_detector():
    global detector
    if detector is None:
        from .detector import YOLODetector

        detector = YOLODetector(settings.preferred_model(), settings.confidence, settings.iou, settings.image_size)
    return detector


def model_ready() -> bool:
    return (root / settings.preferred_model()).exists()


def model_status() -> dict[str, object]:
    custom = root / settings.custom_model_path
    base = root / settings.model_path
    if custom.exists():
        return {"ready": True, "kind": "custom", "message": "Modelo entrenado listo"}
    if base.exists():
        return {"ready": True, "kind": "base", "message": "Modelo base listo. Para carritos especificos falta entrenar toy_car_best.pt"}
    return {
        "ready": False,
        "kind": "missing",
        "message": "Falta descargar yolo11n.pt o entrenar toy_car_best.pt",
    }


def set_camera_source(source: str) -> dict[str, object]:
    global camera, camera_source, camera_stream_version
    if source not in {"webcam", "esp32", "auto"}:
        raise ValueError("La camara debe ser webcam, esp32 o auto.")
    camera_source = source
    camera = build_camera(source)
    camera_stream_version += 1
    return camera_status()


def camera_status() -> dict[str, object]:
    return {
        "source": camera_source,
        "stream_version": camera_stream_version,
        "camera_url": settings.camera_url,
        "webcam_index": settings.webcam_index,
        "use_webcam_fallback": settings.use_webcam_fallback,
        "available_sources": ["webcam", "esp32", "auto"],
    }


def mjpeg_frames():
    try:
        frame_iter = camera.stream_frames()
        for frame in frame_iter:
            ok, encoded = cv2.imencode(".jpg", frame)
            if not ok:
                continue
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + encoded.tobytes() + b"\r\n"
    except Exception as exc:
        frame = placeholder_frame(str(exc))
        ok, encoded = cv2.imencode(".jpg", frame)
        if ok:
            while True:
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + encoded.tobytes() + b"\r\n"


@app.get("/")
def dashboard() -> FileResponse:
    return FileResponse(
        web_dir / "index.html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
        },
    )


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "camera_url": settings.camera_url,
        "camera_source": camera_source,
        "camera_status": camera_status(),
        "webcam_index": settings.webcam_index,
        "use_webcam_fallback": settings.use_webcam_fallback,
        "camera_urls": settings.camera_urls,
        "snapshot_urls": settings.snapshot_urls,
        "model": settings.preferred_model(),
        "model_ready": model_status()["ready"],
        "model_status": model_status(),
        "classes": settings.classes,
    }


@app.get("/snapshot")
def snapshot() -> Response:
    try:
        frame = camera.read_frame()
    except Exception as exc:
        frame = placeholder_frame(str(exc))
    ok, encoded = cv2.imencode(".jpg", frame)
    if not ok:
        raise RuntimeError("No se pudo convertir el frame a JPG.")
    return Response(content=encoded.tobytes(), media_type="image/jpeg")


@app.get("/video_feed")
def video_feed() -> StreamingResponse:
    return StreamingResponse(mjpeg_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/detect/live")
def detect_live():
    try:
        frame = camera.read_frame()
        active_detector = get_detector()
        detections = active_detector.detect(frame)
        counts = controller.count_by_camera_zones(detections, frame.shape[1], frame.shape[0])
        decision = controller.decide_from_counts(counts)
        return {
            "ok": True,
            "count": len(detections),
            "counts": counts,
            "decision": decision.to_dict(),
            "detections": [item.to_dict() for item in detections],
            "model_status": model_status(),
        }
    except Exception as exc:
        sim = simulation.snapshot()
        decision = controller.decide_from_counts(sim["counts"], sim["waiting"])
        return JSONResponse(
            status_code=200,
            content={
                "ok": False,
                "count": 0,
                "counts": sim["counts"],
                "decision": decision.to_dict(),
                "detections": [],
                "model_status": model_status(),
                "error": str(exc),
            },
        )


@app.get("/api/network")
def network() -> dict[str, object]:
    data = parse_network()
    if not data.get("found"):
        sample = root / "sumo" / "sample_intersection.net.xml"
        if sample.exists():
            return parse_network(sample)
    return data


@app.get("/api/status")
def status() -> dict[str, object]:
    network_data = network()
    sim = simulation.snapshot()
    decision = controller.decide_from_counts(sim["counts"], sim["waiting"])
    return {
        "camera_url": settings.camera_url,
        "camera_source": camera_source,
        "camera_status": camera_status(),
        "webcam_index": settings.webcam_index,
        "model": settings.preferred_model(),
        "model_ready": model_status()["ready"],
        "model_status": model_status(),
        "network_found": network_data.get("found", False),
        "edge_count": network_data.get("edge_count", 0),
        "junction_count": network_data.get("junction_count", 0),
        "simulation": sim,
        "decision": decision.to_dict(),
    }


@app.get("/api/camera")
def get_camera() -> dict[str, object]:
    return camera_status()


@app.post("/api/camera/{source}")
def change_camera(source: str):
    try:
        return {"ok": True, "camera": set_camera_source(source)}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/simulation/step")
def simulation_step() -> dict[str, object]:
    current = simulation.snapshot()
    decision = controller.decide_from_counts(current["counts"], current["waiting"])
    sim = simulation.step(decision.green_lane)
    next_decision = controller.decide_from_counts(sim["counts"], sim["waiting"])
    return {"simulation": sim, "decision": next_decision.to_dict()}


@app.post("/api/simulation/reset")
def simulation_reset() -> dict[str, object]:
    sim = simulation.reset()
    decision = controller.decide_from_counts(sim["counts"], sim["waiting"])
    return {"simulation": sim, "decision": decision.to_dict()}


@app.post("/detect")
async def detect_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        array = np.frombuffer(content, dtype=np.uint8)
        frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("El archivo no parece ser una imagen valida.")
        active_detector = get_detector()
        detections = active_detector.detect(frame)
        counts = controller.count_by_camera_zones(detections, frame.shape[1], frame.shape[0])
        decision = controller.decide_from_counts(counts)
        return {
            "ok": True,
            "count": len(detections),
            "counts": counts,
            "decision": decision.to_dict(),
            "detections": [item.to_dict() for item in detections],
            "model_status": model_status(),
        }
    except Exception as exc:
        return JSONResponse(
            status_code=200,
            content={
                "ok": False,
                "count": 0,
                "detections": [],
                "model_status": model_status(),
                "error": str(exc),
            },
        )
