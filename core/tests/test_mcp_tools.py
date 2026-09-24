"""
Unit tests for AuraStream MCP tools conforming to MCP Spec 2025-11-25+.
"""

import json
from core.app.mcp.server import (
    get_scene_telemetry,
    analyze_frame_multimodal,
    adapt_household_ambient,
    generate_spoiler_free_recap,
)


def test_mcp_tool_get_scene_telemetry():
    result_json = get_scene_telemetry(timestamp=15.0, stream_id="stream_aurora_voyager")
    data = json.loads(result_json)
    assert data["stream_id"] == "stream_aurora_voyager"
    assert "actors_in_scene" in data
    assert len(data["actors_in_scene"]) >= 1


def test_mcp_tool_analyze_frame():
    result_json = analyze_frame_multimodal(
        timestamp=20.0,
        user_query="Who is this character?",
        stream_id="stream_aurora_voyager",
    )
    data = json.loads(result_json)
    assert "summary" in data
    assert "trivia_cards" in data
    assert len(data["trivia_cards"]) >= 1


def test_mcp_tool_adapt_household():
    result_json = adapt_household_ambient(
        viewer_profile="family",
        ambient_noise_level="loud",
        content_rating_cap="PG",
    )
    data = json.loads(result_json)
    assert data["status"] == "applied"
    assert data["fire_tv_commands"]["subtitle_size"] == "large"
    assert data["fire_tv_commands"]["dialogue_boost_db"] > 0


def test_mcp_tool_spoiler_free_recap():
    result_json = generate_spoiler_free_recap(
        current_time=75.0,
        stream_id="stream_aurora_voyager",
    )
    data = json.loads(result_json)
    assert data["current_position_seconds"] == 75.0
    assert "spoiler_free_summary" in data
