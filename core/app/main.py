"""
AuraStream FastAPI & MCP Application Server.
Hosts the Streamable HTTP MCP Server and serves the Fire TV / Vega OS Web Client.
"""

import os
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

from .mcp.server import mcp_server, mcp_asgi_app
from .aws.telemetry import get_telemetry_for_timestamp
from .aws.bedrock import bedrock_engine
from .models.schemas import (
    MultiModalAnalysisRequest,
    MultiModalAnalysisResponse,
    SceneTelemetry,
    AmbientProfile,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CLIENT_DIR = BASE_DIR / "client"

app = FastAPI(
    title="AuraStream: Living Room Intelligence Engine",
    description="Amazon Developer Hackathon - Fire TV & Alexa+ Streamable HTTP MCP Server",
    version="1.0.0",
)

# Enable CORS for Fire TV Simulator and Cross-Origin TV devices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health and readiness probe."""
    return {
        "status": "healthy",
        "service": "AuraStream Living Room Intelligence",
        "mcp_version": "2025-11-25+ Streamable HTTP",
        "aws_bedrock_region": bedrock_engine.region_name,
        "primary_track": "Fire TV (AI-Enhanced Viewing & Multi-Modal UX)",
        "mini_challenges": ["AWS Builder", "Open Source"],
    }


@app.get("/api/telemetry", response_model=SceneTelemetry)
async def api_get_telemetry(
    timestamp: float = Query(..., ge=0.0, description="Video timestamp in seconds"),
    stream_id: str = Query(default="stream_aurora_voyager", description="Stream ID"),
):
    """Retrieve scene telemetry for current video playback."""
    return get_telemetry_for_timestamp(stream_id, timestamp)


@app.post("/api/multimodal-query", response_model=MultiModalAnalysisResponse)
async def api_multimodal_query(request: MultiModalAnalysisRequest):
    """Execute multi-modal frame reasoning via Amazon Bedrock."""
    return bedrock_engine.analyze_frame_and_query(request)


@app.post("/api/ambient-adapt")
async def api_ambient_adapt(profile: AmbientProfile):
    """Apply adaptive audio, subtitle, and rating constraints to Fire TV."""
    return {
        "status": "applied",
        "profile": profile.model_dump(),
        "fire_tv_commands": {
            "dialogue_boost_db": +4.5 if profile.dialogue_enhancement else 0.0,
            "subtitles_enabled": profile.subtitles_adaptive,
            "subtitle_size": "large" if profile.ambient_noise_level == "loud" else "medium",
            "content_safety_filter": profile.content_rating_cap,
        },
    }


# Mount the MCP Streamable HTTP ASGI app at /mcp
app.mount("/mcp", mcp_asgi_app)

# Mount client assets for Fire TV web app
if CLIENT_DIR.exists():
    css_dir = CLIENT_DIR / "css"
    js_dir = CLIENT_DIR / "js"
    assets_dir = CLIENT_DIR / "assets"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    
    app.mount("/static", StaticFiles(directory=str(CLIENT_DIR)), name="static")

    @app.get("/")
    async def serve_fire_tv_client():
        index_file = CLIENT_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return JSONResponse({"message": "Fire TV client index.html initializing..."})

    @app.get("/favicon.ico")
    async def favicon():
        return JSONResponse({"status": "ok"}, status_code=204)

