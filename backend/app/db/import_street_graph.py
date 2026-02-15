from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.models import StreetEdge, StreetNode

SAMPLE_GRAPH_PATH = Path(__file__).resolve().parent / "datasets" / "street_graph_sevilla.sample.json"


def _point_wkt(lat: float, lng: float) -> str:
    return f"POINT({lng} {lat})"


def _line_wkt(points: list[list[float]]) -> str:
    pairs = ", ".join(f"{lng} {lat}" for lat, lng in points)
    return f"LINESTRING({pairs})"


def import_graph(db: Session, dataset_path: Path = SAMPLE_GRAPH_PATH) -> dict[str, int]:
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    nodes = payload.get("nodes", [])
    edges = payload.get("edges", [])

    db.query(StreetEdge).delete()
    db.query(StreetNode).delete()

    for node in nodes:
        db.add(
            StreetNode(
                id=node["id"],
                geom=_point_wkt(node["lat"], node["lng"]),
            )
        )

    for edge in edges:
        db.add(
            StreetEdge(
                id=edge.get("id", str(uuid.uuid4())),
                source_node=edge["source_node"],
                target_node=edge["target_node"],
                geom=_line_wkt(edge["geometry"]),
                length_m=edge["length_m"],
                width_estimate=edge.get("width_estimate"),
                highway_type=edge.get("highway_type"),
                is_walkable=edge.get("is_walkable", True),
                tags=json.dumps(edge.get("tags", {})),
            )
        )

    db.commit()
    return {"nodes": len(nodes), "edges": len(edges)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Import walkable Sevilla street graph")
    parser.add_argument("--dataset", type=Path, default=SAMPLE_GRAPH_PATH)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        summary = import_graph(db, dataset_path=args.dataset)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
