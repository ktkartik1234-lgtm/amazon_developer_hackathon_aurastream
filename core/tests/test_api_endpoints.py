"""
Integration tests for AuraStream FastAPI endpoints.
"""

from fastapi.testclient import TestClient
from core.app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "Fire TV" in data["primary_track"]


def test_api_telemetry_endpoint():
    res = client.get("/api/telemetry?stream_id=stream_sintel&timestamp=10.0")
    assert res.status_code == 200
    data = res.json()
    assert data["stream_id"] == "stream_sintel"
    assert data["title"] == "Sintel: The Dragon's Ascent"
    assert len(data["actors_in_scene"]) >= 1
    assert any("Sintel" in a["name"] for a in data["actors_in_scene"])

    # Test sports stream
    res_sports = client.get("/api/telemetry?stream_id=stream_sports&timestamp=15.0")
    assert res_sports.status_code == 200
    assert res_sports.json()["genre"] == "Live Sports / Football"


def test_api_multimodal_query_endpoint():
    payload = {
        "timestamp": 25.0,
        "stream_id": "stream_aurora_voyager",
        "user_query": "What objects are visible?",
    }
    res = client.post("/api/multimodal-query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "trivia_cards" in data


def test_api_ambient_adapt_endpoint():
    payload = {
        "viewer_profile": "late_night",
        "ambient_noise_level": "quiet",
        "content_rating_cap": "R",
        "subtitles_adaptive": True,
        "dialogue_enhancement": True,
    }
    res = client.post("/api/ambient-adapt", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "applied"
    assert "fire_tv_commands" in data


def test_fire_tv_client_static_assets():
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert "AuraStream" in res_index.text

    res_css = client.get("/css/style.css")
    assert res_css.status_code == 200
    assert "--amazon-cyan" in res_css.text

    res_js = client.get("/js/spatialNav.js")
    assert res_js.status_code == 200
    assert "SpatialNavigationManager" in res_js.text

    res_video = client.get("/js/videoPlayer.js")
    assert res_video.status_code == 200

    res_favicon = client.get("/favicon.ico")
    assert res_favicon.status_code in [200, 204]

