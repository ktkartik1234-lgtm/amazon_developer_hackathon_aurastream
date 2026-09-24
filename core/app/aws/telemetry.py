"""
Scene Telemetry & Timeline Knowledge Engine for AuraStream.
Provides continuous scene contextualization across playback timestamps.
Loads canonical telemetry from data/scenes.json (Single Source of Truth).
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from ..models.schemas import SceneTelemetry, SceneActor, SceneObject

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "scenes.json"


def _load_canonical_scenes() -> Dict[str, Dict[str, Any]]:
    """Load canonical scenes database from JSON file and parse into model dictionaries."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Canonical scenes database missing at {DATA_PATH}")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw_db: Dict[str, Dict[str, Any]] = json.load(f)

    parsed_db: Dict[str, Dict[str, Any]] = {}
    for stream_id, data in raw_db.items():
        parsed_timeline = []
        for entry in data.get("timeline", []):
            actors = [
                SceneActor(
                    name=a["name"],
                    character=a["character"],
                    bio_snippet=a.get("bio_snippet", ""),
                    confidence=float(a.get("confidence", 0.95)),
                )
                for a in entry.get("actors", [])
            ]
            objects = [
                SceneObject(
                    label=o["label"],
                    category=o.get("category", "General"),
                    bounding_box=o.get("bounding_box"),
                )
                for o in entry.get("objects", [])
            ]
            parsed_timeline.append({
                "time_range": tuple(entry["time_range"]),
                "actors": actors,
                "objects": objects,
                "soundtrack": entry.get("soundtrack"),
                "trivia_fact": entry.get("trivia_fact"),
                "sports_telemetry": entry.get("sports_telemetry"),
                "plot_summary": entry.get("plot_summary", ""),
                "subtitles": entry.get("subtitles"),
            })

        parsed_db[stream_id] = {
            "title": data["title"],
            "genre": data["genre"],
            "timeline": parsed_timeline,
        }

    return parsed_db


# Global canonical database
SCENE_DATABASE: Dict[str, Dict[str, Any]] = _load_canonical_scenes()


def get_telemetry_for_timestamp(stream_id: str, timestamp: float) -> SceneTelemetry:
    """
    Retrieve telemetry for a given stream and timestamp with fallback.
    """
    # Fallback to stream_sintel as primary default if stream_id not found
    stream_data = SCENE_DATABASE.get(
        stream_id,
        SCENE_DATABASE.get("stream_sintel", SCENE_DATABASE.get("stream_aurora_voyager")),
    )
    title = stream_data["title"]
    genre = stream_data["genre"]

    # Match time range
    matched_entry: Optional[Dict[str, Any]] = None
    for entry in stream_data.get("timeline", []):
        t_start, t_end = entry["time_range"]
        if t_start <= timestamp <= t_end:
            matched_entry = entry
            break

    # If past timeline range, clamp to last entry
    if not matched_entry and stream_data.get("timeline"):
        matched_entry = stream_data["timeline"][-1]

    if matched_entry:
        return SceneTelemetry(
            timestamp=timestamp,
            stream_id=stream_id,
            title=title,
            genre=genre,
            actors_in_scene=matched_entry.get("actors", []),
            objects_in_scene=matched_entry.get("objects", []),
            soundtrack=matched_entry.get("soundtrack"),
            trivia_fact=matched_entry.get("trivia_fact"),
            sports_telemetry=matched_entry.get("sports_telemetry"),
            subtitles=matched_entry.get("subtitles"),
        )

    return SceneTelemetry(
        timestamp=timestamp,
        stream_id=stream_id,
        title=title,
        genre=genre,
        actors_in_scene=[],
        objects_in_scene=[],
    )
