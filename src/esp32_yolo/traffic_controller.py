from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from .detector import Detection


@dataclass(slots=True)
class LaneDemand:
    lane_id: str
    label: str
    vehicle_count: int = 0
    waiting_time: float = 0.0
    emergency_priority: float = 0.0

    @property
    def score(self) -> float:
        return self.vehicle_count + self.waiting_time * 0.25 + self.emergency_priority * 3.0


@dataclass(slots=True)
class SignalDecision:
    green_lane: str
    green_label: str
    green_seconds: int
    yellow_seconds: int
    reason: str
    demands: list[LaneDemand]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["demands"] = [asdict(item) | {"score": item.score} for item in self.demands]
        return data


class TrafficLightController:
    def __init__(self, config_path: str | Path = "configs/traffic_lights.yaml") -> None:
        self.config_path = Path(config_path)
        with self.config_path.open("r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file) or {}

    def decide_from_counts(self, counts: dict[str, int], waiting: dict[str, float] | None = None) -> SignalDecision:
        waiting = waiting or {}
        lanes = self.config.get("lanes", {})
        min_green = int(self.config.get("min_green_seconds", 8))
        max_green = int(self.config.get("max_green_seconds", 45))
        yellow = int(self.config.get("yellow_seconds", 3))

        demands: list[LaneDemand] = []
        for lane_id, lane_data in lanes.items():
            demands.append(
                LaneDemand(
                    lane_id=lane_id,
                    label=str(lane_data.get("label", lane_id)),
                    vehicle_count=int(counts.get(lane_id, 0)),
                    waiting_time=float(waiting.get(lane_id, 0.0)),
                )
            )

        if not demands:
            demands = [LaneDemand("default", "Principal", sum(counts.values()))]

        winner = max(demands, key=lambda item: item.score)
        total = max(1, sum(item.vehicle_count for item in demands))
        share = winner.vehicle_count / total
        green = min(max_green, max(min_green, int(min_green + share * (max_green - min_green))))
        reason = f"Mayor demanda: {winner.vehicle_count} vehiculos en {winner.label}."

        return SignalDecision(winner.lane_id, winner.label, green, yellow, reason, demands)

    def count_by_camera_zones(self, detections: list[Detection], frame_width: int, frame_height: int) -> dict[str, int]:
        lanes = self.config.get("lanes", {})
        counts = {lane_id: 0 for lane_id in lanes}
        for detection in detections:
            x1, y1, x2, y2 = detection.xyxy
            cx = ((x1 + x2) / 2) / max(1, frame_width)
            cy = ((y1 + y2) / 2) / max(1, frame_height)
            for lane_id, lane_data in lanes.items():
                zone = lane_data.get("camera_zone", [0, 0, 1, 1])
                zx1, zy1, zx2, zy2 = [float(value) for value in zone]
                if zx1 <= cx <= zx2 and zy1 <= cy <= zy2:
                    counts[lane_id] += 1
        return counts
