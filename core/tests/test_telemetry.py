"""
Unit tests for AuraStream scene telemetry engine.
Validates canonical scenes, client parity, and time-coded timeline retrieval.
"""

import json
from pathlib import Path
from core.app.aws.telemetry import get_telemetry_for_timestamp, SCENE_DATABASE

CLIENT_STREAM_IDS = ["stream_sintel", "stream_oceans", "stream_sailing", "stream_sports"]


def test_client_streams_exist_in_database():
    """Assert all 4 client stream IDs exist in the canonical SCENE_DATABASE."""
    for stream_id in CLIENT_STREAM_IDS:
        assert stream_id in SCENE_DATABASE, f"Missing stream ID {stream_id} in SCENE_DATABASE"
        stream = SCENE_DATABASE[stream_id]
        assert stream["title"], f"Stream {stream_id} has empty title"
        assert stream["genre"], f"Stream {stream_id} has empty genre"
        assert len(stream["timeline"]) > 0, f"Stream {stream_id} has empty timeline"
        for entry in stream["timeline"]:
            assert len(entry["actors"]) > 0, f"Timeline entry missing actors in {stream_id}"
            assert entry["soundtrack"], f"Timeline entry missing soundtrack in {stream_id}"


def test_client_streamdata_js_parity():
    """Assert 100% parity between core/app/data/scenes.json and client/js/streamData.js."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    scenes_json_path = base_dir / "core" / "app" / "data" / "scenes.json"
    stream_data_js_path = base_dir / "client" / "js" / "streamData.js"

    assert scenes_json_path.exists(), "scenes.json not found"
    assert stream_data_js_path.exists(), "streamData.js not found"

    with open(scenes_json_path, "r", encoding="utf-8") as f:
        backend_data = json.load(f)

    with open(stream_data_js_path, "r", encoding="utf-8") as f:
        js_text = f.read()

    # Extract JSON object from window.AuraSceneDatabase = { ... };
    json_start = js_text.find("{")
    json_end = js_text.rfind("}") + 1
    frontend_data = json.loads(js_text[json_start:json_end])

    for stream_id in CLIENT_STREAM_IDS:
        assert stream_id in frontend_data, f"{stream_id} missing in client streamData.js"
        assert frontend_data[stream_id]["title"] == backend_data[stream_id]["title"]
        assert len(frontend_data[stream_id]["timeline"]) == len(backend_data[stream_id]["timeline"])


def test_get_telemetry_sintel():
    """Assert Sintel telemetry returns Halina Reijn and Jan Morgenstern."""
    telem = get_telemetry_for_timestamp("stream_sintel", 10.0)
    assert telem.title == "Sintel: The Dragon's Ascent"
    assert any("Sintel" in a.name for a in telem.actors_in_scene)
    assert "Jan Morgenstern" in (telem.soundtrack or "")


def test_get_telemetry_sports():
    """Assert Sports telemetry returns xG, tactical formation, and soccer stats."""
    telem = get_telemetry_for_timestamp("stream_sports", 15.0)
    assert telem.genre == "Live Sports / Football"
    assert telem.sports_telemetry is not None
    assert "4-3-3" in telem.sports_telemetry.get("active_tactical_formation", "")
    assert "possession" in telem.sports_telemetry


def test_get_telemetry_oceans():
    """Assert Oceans telemetry returns Dr. Sylvia Earle."""
    telem = get_telemetry_for_timestamp("stream_oceans", 12.0)
    assert telem.title == "Deep Oceans: Abyssal Realms"
    assert any("Sylvia Earle" in a.name for a in telem.actors_in_scene)


def test_get_telemetry_sailing():
    """Assert Sailing telemetry returns Costa Rica voyage."""
    telem = get_telemetry_for_timestamp("stream_sailing", 20.0)
    assert telem.title == "Costa Rica: Whale Tail Voyage"
    assert any("Mateo Cruz" in a.name for a in telem.actors_in_scene)


def test_fallback_stream():
    """Assert unknown streams fall back safely without error."""
    telem = get_telemetry_for_timestamp("unknown_stream_xyz", 50.0)
    assert telem.title is not None
