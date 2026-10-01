"""
Model Context Protocol (MCP) Server for AuraStream.
Conforms to MCP Specification 2025-11-25+ over Streamable HTTP Transport.
Exposes living room intelligence and scene comprehension tools to Alexa+ and TV clients.
"""

import json
from typing import Dict, Any, Optional
from mcp.server.mcpserver import MCPServer
from ..aws.telemetry import get_telemetry_for_timestamp, SCENE_DATABASE
from ..aws.bedrock import bedrock_engine
from ..commands import command_bus, CommandValidationError
from ..models.schemas import (
    MultiModalAnalysisRequest,
    AmbientProfile,
)

# Initialize MCP Server conforming to 2025-11-25+ spec
mcp_server = MCPServer(
    name="AuraStream Living Room Intelligence",
    instructions=(
        "AuraStream provides ambient real-time scene comprehension, multi-modal frame analysis, "
        "and interactive living room intelligence for Amazon Fire TV and Alexa+."
    ),
    version="1.0.0",
)


@mcp_server.tool()
def get_scene_telemetry(timestamp: float, stream_id: str = "stream_sintel") -> str:
    """
    Retrieve live scene telemetry for video playback, including characters on screen,
    objects detected, current soundtrack, and production trivia facts.
    """
    telemetry = get_telemetry_for_timestamp(stream_id, timestamp)
    return telemetry.model_dump_json(indent=2)


@mcp_server.tool()
def analyze_frame_multimodal(
    timestamp: float,
    user_query: str,
    stream_id: str = "stream_sintel",
    image_base64: str = "",
) -> str:
    """
    Execute multi-modal visual reasoning on the current Fire TV video frame using Amazon Bedrock.
    Analyzes character expressions, background environments, sports plays, and user questions.
    """
    req = MultiModalAnalysisRequest(
        timestamp=timestamp,
        stream_id=stream_id,
        user_query=user_query,
        image_base64=image_base64 if image_base64 else None,
    )
    res = bedrock_engine.analyze_frame_and_query(req)
    return res.model_dump_json(indent=2)


@mcp_server.tool()
def adapt_household_ambient(
    viewer_profile: str = "family",
    ambient_noise_level: str = "medium",
    content_rating_cap: str = "PG-13",
) -> str:
    """
    Context-aware adaptation of the living room entertainment experience.
    Dynamically tunes subtitle sizing, audio dynamic range compression (Night Mode),
    and age-appropriate scene filtering for family viewing.
    """
    profile = AmbientProfile(
        viewer_profile=viewer_profile,
        ambient_noise_level=ambient_noise_level,
        content_rating_cap=content_rating_cap,
        subtitles_adaptive=(ambient_noise_level in ["medium", "loud"]),
        dialogue_enhancement=(viewer_profile in ["family", "late_night"]),
    )

    adaptations = {
        "status": "applied",
        "profile": profile.model_dump(),
        "fire_tv_commands": {
            "dialogue_boost_db": +4.5 if profile.dialogue_enhancement else 0.0,
            "subtitles_enabled": profile.subtitles_adaptive,
            "subtitle_size": "large" if ambient_noise_level == "loud" else "medium",
            "content_safety_filter": content_rating_cap,
        },
        "reasoning": f"Optimized living room acoustics and visual overlays for '{viewer_profile}' viewing with '{ambient_noise_level}' ambient sound.",
    }
    return json.dumps(adaptations, indent=2)


@mcp_server.tool()
def generate_spoiler_free_recap(
    current_time: float,
    stream_id: str = "stream_sintel",
) -> str:
    """
    Generate an instant, spoiler-free recap of the storyline up to the current timestamp.
    Guarantees no future plot points beyond the viewer's current playback position are revealed.
    """
    telemetry = get_telemetry_for_timestamp(stream_id, current_time)
    stream_data = SCENE_DATABASE.get(
        stream_id,
        SCENE_DATABASE.get("stream_sintel", SCENE_DATABASE.get("stream_aurora_voyager", {})),
    )

    # Accumulate plot points and characters strictly up to current_time
    seen_plots = []
    characters_seen = set()
    for entry in stream_data.get("timeline", []):
        t_start, _ = entry["time_range"]
        if current_time >= t_start:
            if entry.get("plot_summary"):
                seen_plots.append(entry["plot_summary"])
            for a in entry.get("actors", []):
                characters_seen.add(a.name)

    summary_text = (
        " ".join(seen_plots)
        if seen_plots
        else f"Viewing position {int(current_time // 60)}m {int(current_time % 60)}s in {telemetry.title}."
    )

    recap = {
        "title": telemetry.title,
        "current_position_seconds": current_time,
        "spoiler_free_summary": f"Up to {int(current_time // 60)}m {int(current_time % 60)}s: {summary_text}",
        "key_characters_seen": sorted(list(characters_seen)),
        "genre": telemetry.genre,
    }
    return json.dumps(recap, indent=2)


@mcp_server.tool()
def dispatch_fire_tv_command(command: str, argument: str = "") -> str:
    """
    Dispatch a remote-control command to the paired Fire TV client over the
    AuraStream command bus (Server-Sent Events). Lets Alexa+ actually drive the
    living room TV instead of only describing controls.

    Supported commands:
      play | pause | toggle_playback | seek_forward | seek_back | restart
      switch_stream (argument = stream_id, e.g. stream_sports)
      open_xray | toggle_subtitles | hide_hud
    """
    try:
        event = command_bus.dispatch(command, argument or None, source="alexa_plus_mcp")
    except CommandValidationError as err:
        return json.dumps({"status": "rejected", "error": str(err)}, indent=2)

    result = {
        "status": "dispatched",
        "event": event,
        "delivery": "Fire TV client consumes commands via SSE at /api/events",
        "queue_depth": command_bus.depth(),
    }
    return json.dumps(result, indent=2)


# Build the ASGI streamable HTTP app
mcp_asgi_app = mcp_server.streamable_http_app(streamable_http_path="/mcp")
