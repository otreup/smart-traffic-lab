from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class CaptureSettings:
    output_dir: str = "data/raw"
    prefix: str = "toy_car"


@dataclass(slots=True)
class ApiSettings:
    host: str = "0.0.0.0"
    port: int = 8000


@dataclass(slots=True)
class AppSettings:
    camera_url: str
    camera_source: str
    camera_urls: list[str]
    snapshot_urls: list[str]
    fallback_camera_url: str | None
    use_webcam_fallback: bool
    webcam_index: int
    model_path: str
    custom_model_path: str
    confidence: float
    iou: float
    image_size: int
    classes: list[str]
    capture: CaptureSettings
    api: ApiSettings

    def preferred_model(self) -> str:
        custom_path = Path(self.custom_model_path)
        if custom_path.exists():
            return str(custom_path)
        return self.model_path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_settings(path: str | Path | None = None) -> AppSettings:
    settings_path = Path(path) if path else _project_root() / "configs" / "settings.yaml"
    with settings_path.open("r", encoding="utf-8") as file:
        data: dict[str, Any] = yaml.safe_load(file) or {}

    capture_data = data.get("capture") or {}
    api_data = data.get("api") or {}

    return AppSettings(
        camera_url=str(data.get("camera_url", "http://192.168.1.44")),
        camera_source=str(data.get("camera_source", "auto")),
        camera_urls=list(data.get("camera_urls", [data.get("camera_url", "http://192.168.1.44")])),
        snapshot_urls=list(data.get("snapshot_urls", [data.get("camera_url", "http://192.168.1.44/capture")])),
        fallback_camera_url=data.get("fallback_camera_url"),
        use_webcam_fallback=bool(data.get("use_webcam_fallback", True)),
        webcam_index=int(data.get("webcam_index", 0)),
        model_path=str(data.get("model_path", "yolo11n.pt")),
        custom_model_path=str(data.get("custom_model_path", "models/toy_car_best.pt")),
        confidence=float(data.get("confidence", 0.35)),
        iou=float(data.get("iou", 0.45)),
        image_size=int(data.get("image_size", 640)),
        classes=list(data.get("classes", ["toy_car"])),
        capture=CaptureSettings(
            output_dir=str(capture_data.get("output_dir", "data/raw")),
            prefix=str(capture_data.get("prefix", "toy_car")),
        ),
        api=ApiSettings(
            host=str(api_data.get("host", "0.0.0.0")),
            port=int(api_data.get("port", 8000)),
        ),
    )
