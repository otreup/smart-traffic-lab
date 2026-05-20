from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from time import sleep
from collections.abc import Iterator
from urllib.request import urlopen

import cv2
import numpy as np


@dataclass(slots=True)
class CameraClient:
    url: str
    fallback_url: str | None = None
    urls: list[str] = field(default_factory=list)
    snapshot_urls: list[str] = field(default_factory=list)
    source: str = "auto"
    webcam_index: int = 0
    use_webcam_fallback: bool = True
    width: int | None = None
    height: int | None = None

    def open(self) -> cv2.VideoCapture:
        tried: list[str] = []
        if self.source in {"auto", "esp32"}:
            for url in self._candidate_urls():
                tried.append(url)
                capture = self._open_url(url)
                if capture.isOpened():
                    ok, frame = capture.read()
                    if ok and frame is not None:
                        return capture
                capture.release()

        if self.source == "webcam" or (self.source == "auto" and self.use_webcam_fallback):
            capture = self._open_webcam(tried)
            if capture.isOpened():
                ok, frame = capture.read()
                if ok and frame is not None:
                    return capture
            capture.release()

        raise RuntimeError(f"No se pudo abrir ninguna camara. Rutas probadas: {', '.join(tried)}")

    def read_frame(self) -> np.ndarray:
        if self.source in {"auto", "esp32"}:
            snapshot = self._read_snapshot()
            if snapshot is not None:
                return snapshot

        capture = self.open()
        try:
            ok, frame = capture.read()
            if not ok or frame is None:
                sleep(0.2)
                ok, frame = capture.read()
            if not ok or frame is None:
                raise RuntimeError("La camara abrio, pero no entrego ningun frame.")
            return frame
        finally:
            capture.release()

    def save_snapshot(self, output_path: str | Path) -> Path:
        frame = self.read_frame()
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(path), frame)
        return path

    def stream_frames(self) -> Iterator[np.ndarray]:
        capture = self.open()
        try:
            while True:
                ok, frame = capture.read()
                if not ok or frame is None:
                    sleep(0.05)
                    continue
                yield frame
        finally:
            capture.release()

    def _open_url(self, url: str) -> cv2.VideoCapture:
        capture = cv2.VideoCapture(url)
        if self.width:
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height:
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        return capture

    def _open_webcam(self, tried: list[str]) -> cv2.VideoCapture:
        backends = [
            ("directshow", cv2.CAP_DSHOW),
            ("mediafoundation", cv2.CAP_MSMF),
            ("default", cv2.CAP_ANY),
        ]
        for name, backend in backends:
            tried.append(f"webcam:{self.webcam_index}:{name}")
            capture = cv2.VideoCapture(self.webcam_index, backend)
            if capture.isOpened():
                return capture
            capture.release()
        return cv2.VideoCapture(-1)

    def _candidate_urls(self) -> list[str]:
        urls = [self.url, *self.urls]
        if self.fallback_url:
            urls.append(self.fallback_url)
        return list(dict.fromkeys(urls))

    def _read_snapshot(self) -> np.ndarray | None:
        for url in self.snapshot_urls:
            try:
                with urlopen(url, timeout=2.0) as response:
                    data = np.asarray(bytearray(response.read()), dtype=np.uint8)
                    frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
                    if frame is not None:
                        return frame
            except Exception:
                continue
        return None
