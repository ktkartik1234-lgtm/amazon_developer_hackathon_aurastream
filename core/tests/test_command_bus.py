"""
Tests for the AuraStream Fire TV Command Bus (Alexa+ -> TV control channel).
Covers the in-memory bus, the REST dispatch endpoint, and the SSE event stream.
"""

import asyncio
import json

import pytest
from fastapi.testclient import TestClient

from core.app.commands import command_bus, COMMAND_SET
from core.app.main import app, fire_tv_command_stream

client = TestClient(app)


# ---------------------------------------------------------------------------
# Unit tests: FireTVCommandBus
# ---------------------------------------------------------------------------

def test_bus_dispatch_assigns_monotonic_event_ids():
    before = command_bus.latest_event_id()
    e1 = command_bus.dispatch("pause", source="pytest")
    e2 = command_bus.dispatch("play", source="pytest")
    assert e2["event_id"] == e1["event_id"] + 1
    assert e1["event_id"] > before
    assert e1["command"] == "pause"
    assert e1["source"] == "pytest"
    assert "issued_at" in e1


def test_bus_normalizes_command_and_blank_argument():
    event = command_bus.dispatch("  PAUSE  ", argument="   ")
    assert event["command"] == "pause"
    assert event["argument"] is None


def test_bus_rejects_unknown_command():
    with pytest.raises(ValueError):
        command_bus.dispatch("launch_missile")


def test_bus_requires_argument_for_switch_stream():
    with pytest.raises(ValueError):
        command_bus.dispatch("switch_stream")
    # And succeeds when the stream id is supplied
    event = command_bus.dispatch("switch_stream", argument="stream_sports")
    assert event["argument"] == "stream_sports"


def test_bus_events_since_filters_by_id():
    e1 = command_bus.dispatch("seek_forward", source="pytest")
    e2 = command_bus.dispatch("seek_back", source="pytest")
    events = command_bus.events_since(e1["event_id"])
    assert [e["event_id"] for e in events] == [e2["event_id"]]


def test_command_set_is_complete():
    assert {"play", "pause", "toggle_playback", "seek_forward", "seek_back",
            "restart", "switch_stream", "open_xray", "toggle_subtitles",
            "hide_hud"} == COMMAND_SET


# ---------------------------------------------------------------------------
# Integration tests: REST endpoints
# ---------------------------------------------------------------------------

def test_health_reports_command_bus():
    res = client.get("/health")
    assert res.status_code == 200
    bus_info = res.json()["fire_tv_command_bus"]
    assert bus_info["status"] == "enabled"
    assert "pause" in bus_info["supported_commands"]


def test_remote_command_endpoint_dispatches():
    res = client.post(
        "/api/remote-command",
        json={"command": "pause", "argument": None, "source": "pytest_rest"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "dispatched"
    assert data["event"]["command"] == "pause"
    assert data["event"]["source"] == "pytest_rest"
    assert data["queue_depth"] >= 1


def test_remote_command_endpoint_rejects_unknown_command():
    res = client.post("/api/remote-command", json={"command": "explode"})
    assert res.status_code == 422
    assert "Supported" in res.json()["detail"]


def test_remote_command_endpoint_requires_stream_argument():
    res = client.post("/api/remote-command", json={"command": "switch_stream"})
    assert res.status_code == 422


def test_events_route_is_registered():
    paths = {getattr(route, "path", None) for route in app.routes}
    assert "/api/events" in paths
    assert "/api/remote-command" in paths


def test_sse_generator_emits_dispatched_command():
    # Dispatch BEFORE subscribing. Earlier tests may have queued events too,
    # so drain the whole queue and verify our event arrives among the chunks.
    event = command_bus.dispatch("toggle_subtitles", source="pytest_sse")
    pending = command_bus.events_since(0)
    assert pending, "queue should contain the dispatched event"

    async def collect_all_pending():
        gen = fire_tv_command_stream(0)
        chunks = []
        for _ in range(len(pending)):
            chunks.append(await gen.__anext__())
        await gen.aclose()  # stop the otherwise-infinite SSE stream
        return chunks

    chunks = asyncio.run(collect_all_pending())
    assert len(chunks) == len(pending)
    ours = [c for c in chunks if c["id"] == str(event["event_id"])]
    assert ours, "dispatched event missing from SSE stream"
    payload = json.loads(ours[0]["data"])
    assert payload["command"] == "toggle_subtitles"
    assert payload["source"] == "pytest_sse"


def test_sse_generator_respects_since_cursor():
    stale = command_bus.dispatch("play", source="pytest_sse")
    fresh = command_bus.dispatch("pause", source="pytest_sse")

    async def collect_first_payload():
        gen = fire_tv_command_stream(stale["event_id"])
        first = await gen.__anext__()
        await gen.aclose()
        return first

    chunk = asyncio.run(collect_first_payload())
    assert chunk["id"] == str(fresh["event_id"])  # stale event excluded


def test_sse_generator_skips_history_for_fresh_subscription():
    # A fresh subscriber (cursor at latest) must not replay the bus history.
    stale = command_bus.dispatch("seek_back", source="pytest_sse")
    fresh_cursor = command_bus.latest_event_id()

    async def run():
        newer = command_bus.dispatch("open_xray", source="pytest_sse")
        gen = fire_tv_command_stream(fresh_cursor)
        first = await gen.__anext__()
        await gen.aclose()
        return newer, first

    newer, chunk = asyncio.run(run())
    assert chunk["id"] == str(newer["event_id"])
    assert chunk["id"] != str(stale["event_id"])
