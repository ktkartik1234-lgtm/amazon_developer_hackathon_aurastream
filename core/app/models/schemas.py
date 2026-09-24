"""
Pydantic schemas and data contracts for AuraStream.
Strictly typed for zero-hallucination execution.
"""

import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class SceneActor(BaseModel):
    name: str = Field(..., description="Full name of the actor/character on screen")
    character: str = Field(..., description="Character played in the current scene")
    bio_snippet: str = Field(..., description="Short 1-2 sentence context")
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)


class SceneObject(BaseModel):
    label: str = Field(..., description="Identified object or product in frame")
    category: str = Field(..., description="e.g. Apparel, Tech, Vehicle, Architecture")
    bounding_box: Optional[List[float]] = Field(default=None, description="[ymin, xmin, ymax, xmax]")


class SceneTelemetry(BaseModel):
    timestamp: float = Field(..., description="Current playback timestamp in seconds")
    stream_id: str = Field(..., description="Unique video stream or movie identifier")
    title: str = Field(..., description="Media title")
    genre: str = Field(..., description="Media genre (e.g. Sci-Fi, Sports, Drama)")
    actors_in_scene: List[SceneActor] = Field(default_factory=list)
    objects_in_scene: List[SceneObject] = Field(default_factory=list)
    soundtrack: Optional[str] = Field(default=None, description="Currently playing audio track")
    trivia_fact: Optional[str] = Field(default=None, description="Contextual production fact")
    sports_telemetry: Optional[Dict[str, Any]] = Field(default=None, description="Live player/ball stats if sports")


class TriviaCard(BaseModel):
    card_id: str
    title: str
    headline: str
    description: str
    category: str = Field(..., description="'actor', 'tactics', 'trivia', 'music', 'tech', 'recap', 'navigation'")
    badges: List[str] = Field(default_factory=list)
    interactive_actions: List[str] = Field(default_factory=list)


class MultiModalAnalysisRequest(BaseModel):
    timestamp: float = Field(..., ge=0.0, description="Video timestamp in seconds")
    stream_id: str = Field(..., max_length=128, description="Stream ID")
    user_query: str = Field(..., max_length=1000, description="User voice or remote query")
    image_base64: Optional[str] = None

    @field_validator("user_query")
    @classmethod
    def sanitize_user_query(cls, v: str) -> str:
        # Strip potentially malicious script/HTML injection
        sanitized = re.sub(r"<[^>]*>", "", v).strip()
        return sanitized if sanitized else "What is in this scene?"


class MultiModalAnalysisResponse(BaseModel):
    summary: str
    insights: List[str]
    trivia_cards: List[TriviaCard]
    detected_entities: List[str]
    confidence_score: float
    model_used: str


class AmbientProfile(BaseModel):
    viewer_profile: str = Field(default="family", description="'solo', 'family', 'party', 'late_night'")
    ambient_noise_level: str = Field(default="medium", description="'quiet', 'medium', 'loud'")
    content_rating_cap: str = Field(default="PG-13", description="Maximum rating permitted")
    subtitles_adaptive: bool = True
    dialogue_enhancement: bool = True
