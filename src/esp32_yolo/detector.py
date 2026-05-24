from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from pathlib import Path
from typing import Any

import cv2
import numpy as np

_project_root = Path(__file__).resolve().parents[2]
_ultralytics_config = _project_root / "logs" / "ultralytics"
_ultralytics_config.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("YOLO_CONFIG_DIR", str(_ultralytics_config))

from ultralytics import YOLO


@dataclass(slots=True)
class Detection:
    class_id: int
    label: str
    confidence: float
    xyxy: tuple[float, float, float, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class YOLODetector:
    def __init__(self, model_path: str | Path, confidence: float = 0.35, iou: float = 0.45, image_size: int = 640) -> None:
        self.model = YOLO(str(model_path))
        self.confidence = confidence
        self.iou = iou
        self.image_size = image_size

    def detect(self, frame: np.ndarray) -> list[Detection]:
        results = self.model.predict(
            frame,
            conf=self.confidence,
            iou=self.iou,
            imgsz=self.image_size,
            verbose=False,
        )
        if not results:
            return []

        result = results[0]
        names = result.names
        detections: list[Detection] = []

        for box in result.boxes:
            class_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())
            x1, y1, x2, y2 = [float(value) for value in box.xyxy[0].tolist()]
            detections.append(
                Detection(
                    class_id=class_id,
                    label=str(names.get(class_id, class_id)),
                    confidence=confidence,
                    xyxy=(x1, y1, x2, y2),
                )
            )

        return detections

    def draw(self, frame: np.ndarray, detections: list[Detection]) -> np.ndarray:
        annotated = frame.copy()
        for detection in detections:
            x1, y1, x2, y2 = [int(value) for value in detection.xyxy]
            label = f"{detection.label} {detection.confidence:.2f}"
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 80, 255), 2)
            cv2.putText(
                annotated,
                label,
                (x1, max(y1 - 8, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 80, 255),
                2,
                cv2.LINE_AA,
            )
        return annotated
