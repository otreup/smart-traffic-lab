from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
import xml.etree.ElementTree as ET


@dataclass(slots=True)
class SumoLane:
    id: str
    index: int
    speed: float
    length: float
    shape: list[tuple[float, float]]


@dataclass(slots=True)
class SumoEdge:
    id: str
    from_node: str | None
    to_node: str | None
    lanes: list[SumoLane]


@dataclass(slots=True)
class SumoJunction:
    id: str
    type: str
    x: float
    y: float


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def find_network_file(sumo_dir: str | Path | None = None) -> Path | None:
    base = Path(sumo_dir) if sumo_dir else project_root() / "sumo"
    candidates = [
        base / "sample_intersection.net.xml",
        base / "OSM.net.xml",
        base / "osm.net.xml",
    ]
    candidates.extend(sorted(base.glob("*.net.xml")))
    candidates.extend(sorted(base.glob("*ntxml*")))
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def load_network_xml(path: str | Path) -> str:
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"<net(?=[\s>])[\s\S]*?</net>", text)
    if match:
        return match.group(0)

    if "<net " in text and "</net>" in text:
        start = text.find("<net ")
        end = text.rfind("</net>") + len("</net>")
        return text[start:end]

    raise ValueError(f"No pude encontrar XML SUMO tipo <net> en {path}")


def parse_shape(shape: str | None) -> list[tuple[float, float]]:
    if not shape:
        return []
    points: list[tuple[float, float]] = []
    for pair in shape.split():
        if "," not in pair:
            continue
        x_text, y_text = pair.split(",", 1)
        points.append((float(x_text), float(y_text)))
    return points


def parse_network(path: str | Path | None = None) -> dict[str, object]:
    network_path = Path(path) if path else find_network_file()
    if network_path is None:
        return {
            "found": False,
            "message": "No encontre archivo SUMO. Copia OSM.net.xml o OSM.ntxml.js en la carpeta sumo/.",
            "edges": [],
            "junctions": [],
            "bounds": None,
        }

    xml_text = load_network_xml(network_path)
    root = ET.fromstring(xml_text)

    edges: list[SumoEdge] = []
    junctions: list[SumoJunction] = []
    xs: list[float] = []
    ys: list[float] = []

    for junction in root.findall("junction"):
        junction_type = junction.attrib.get("type", "")
        if junction_type == "internal":
            continue
        x = float(junction.attrib.get("x", 0.0))
        y = float(junction.attrib.get("y", 0.0))
        xs.append(x)
        ys.append(y)
        junctions.append(SumoJunction(junction.attrib.get("id", ""), junction_type, x, y))

    for edge in root.findall("edge"):
        edge_id = edge.attrib.get("id", "")
        if edge_id.startswith(":"):
            continue
        lanes: list[SumoLane] = []
        for lane in edge.findall("lane"):
            shape = parse_shape(lane.attrib.get("shape"))
            for x, y in shape:
                xs.append(x)
                ys.append(y)
            lanes.append(
                SumoLane(
                    id=lane.attrib.get("id", ""),
                    index=int(lane.attrib.get("index", 0)),
                    speed=float(lane.attrib.get("speed", 0.0)),
                    length=float(lane.attrib.get("length", 0.0)),
                    shape=shape,
                )
            )
        if lanes:
            edges.append(SumoEdge(edge_id, edge.attrib.get("from"), edge.attrib.get("to"), lanes))

    bounds = None
    if xs and ys:
        bounds = {"min_x": min(xs), "max_x": max(xs), "min_y": min(ys), "max_y": max(ys)}

    return {
        "found": True,
        "file": str(network_path),
        "edge_count": len(edges),
        "junction_count": len(junctions),
        "bounds": bounds,
        "edges": [asdict(edge) for edge in edges],
        "junctions": [asdict(junction) for junction in junctions],
    }
