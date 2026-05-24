from __future__ import annotations

from dataclasses import asdict, dataclass
import random


@dataclass(slots=True)
class SimVehicle:
    id: str
    lane_id: str
    position: float
    speed: float


class SimpleTrafficSimulation:
    def __init__(self) -> None:
        self.time = 0
        self.vehicles: list[SimVehicle] = []
        self.spawn_counter = 0
        self.lanes = ["north_south", "east_west"]

    def reset(self) -> dict[str, object]:
        self.time = 0
        self.vehicles.clear()
        self.spawn_counter = 0
        return self.snapshot()

    def step(self, green_lane: str | None = None) -> dict[str, object]:
        self.time += 1
        if random.random() < 0.55:
            self.spawn_counter += 1
            lane = random.choice(self.lanes)
            self.vehicles.append(SimVehicle(f"veh_{self.spawn_counter}", lane, 0.0, random.uniform(0.035, 0.085)))

        for vehicle in self.vehicles:
            if green_lane is None or vehicle.lane_id == green_lane or vehicle.position < 0.72:
                vehicle.position += vehicle.speed
            else:
                vehicle.position += vehicle.speed * 0.12

        self.vehicles = [vehicle for vehicle in self.vehicles if vehicle.position < 1.05]
        return self.snapshot()

    def counts(self) -> dict[str, int]:
        return {lane: sum(1 for vehicle in self.vehicles if vehicle.lane_id == lane) for lane in self.lanes}

    def waiting(self) -> dict[str, float]:
        waiting: dict[str, float] = {lane: 0.0 for lane in self.lanes}
        for vehicle in self.vehicles:
            if vehicle.position >= 0.72:
                waiting[vehicle.lane_id] += 1.0
        return waiting

    def snapshot(self) -> dict[str, object]:
        return {
            "time": self.time,
            "counts": self.counts(),
            "waiting": self.waiting(),
            "vehicles": [asdict(vehicle) for vehicle in self.vehicles],
        }
