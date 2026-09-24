"""
Unit tests for AuraStream Pydantic models.
"""

from core.app.models.schemas import (
    SceneActor,
    SceneObject,
    SceneTelemetry,
    TriviaCard,
    MultiModalAnalysisRequest,
    AmbientProfile,
)


def test_scene_actor_schema():
    actor = SceneActor(
        name="Elena Vance",
        character="Astrobiologist",
        bio_snippet="Lead researcher on Europa biosignatures.",
        confidence=0.98,
    )
    assert actor.name == "Elena Vance"
    assert actor.confidence == 0.98
    dumped = actor.model_dump()
    assert dumped["character"] == "Astrobiologist"


def test_scene_telemetry_schema():
    telem = SceneTelemetry(
        timestamp=12.5,
        stream_id="stream_test",
        title="Test Movie",
        genre="Action",
        actors_in_scene=[],
        objects_in_scene=[SceneObject(label="Car", category="Vehicle")],
    )
    assert telem.timestamp == 12.5
    assert len(telem.objects_in_scene) == 1
    assert telem.objects_in_scene[0].label == "Car"


def test_ambient_profile_schema():
    profile = AmbientProfile(
        viewer_profile="family",
        ambient_noise_level="loud",
        content_rating_cap="PG",
    )
    assert profile.content_rating_cap == "PG"
    assert profile.subtitles_adaptive is True
