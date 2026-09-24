"""
Unit tests for Amazon Bedrock vision & multi-modal engine.
Tests intent routing, soundtrack vs tactics disambiguation, and spoiler-free recaps.
"""

from core.app.aws.bedrock import BedrockVisionEngine
from core.app.models.schemas import MultiModalAnalysisRequest


def test_bedrock_multimodal_analysis():
    engine = BedrockVisionEngine(region_name="us-east-1")
    req = MultiModalAnalysisRequest(
        timestamp=20.0,
        stream_id="stream_sintel",
        user_query="Who is on screen?",
    )
    res = engine.analyze_frame_and_query(req)
    assert res.summary is not None
    assert len(res.trivia_cards) >= 1
    assert any("Sintel" in c.title for c in res.trivia_cards)
    assert res.confidence_score > 0.90


def test_bedrock_sports_tactics_analysis():
    engine = BedrockVisionEngine(region_name="us-east-1")
    req = MultiModalAnalysisRequest(
        timestamp=35.0,
        stream_id="stream_sports",
        user_query="Explain this tactical soccer formation",
    )
    res = engine.analyze_frame_and_query(req)
    assert len(res.trivia_cards) >= 1
    assert any(c.category == "tactics" for c in res.trivia_cards)


def test_soundtrack_query_routing():
    """RED TEST: 'What soundtrack is playing?' must route to music, NOT tactics."""
    engine = BedrockVisionEngine(region_name="us-east-1")
    req = MultiModalAnalysisRequest(
        timestamp=15.0,
        stream_id="stream_sintel",
        user_query="What soundtrack is playing right now?",
    )
    res = engine.analyze_frame_and_query(req)
    assert len(res.trivia_cards) >= 1
    assert any(c.category == "music" for c in res.trivia_cards), f"Expected music card, got {[c.category for c in res.trivia_cards]}"
    assert not any(c.category == "tactics" for c in res.trivia_cards), "Keyword 'playing' mistakenly triggered tactics!"


def test_navigation_query_not_tactics():
    """RED TEST: 'Can I play the video?' must NOT trigger soccer tactics."""
    engine = BedrockVisionEngine(region_name="us-east-1")
    req = MultiModalAnalysisRequest(
        timestamp=10.0,
        stream_id="stream_sintel",
        user_query="Can I play the video now?",
    )
    res = engine.analyze_frame_and_query(req)
    assert not any(c.category == "tactics" for c in res.trivia_cards), "Query 'play the video' mistakenly triggered tactics!"


def test_recap_query_routing():
    """RED TEST: 'Catch me up' must return recap cards, not generic trivia."""
    engine = BedrockVisionEngine(region_name="us-east-1")
    req = MultiModalAnalysisRequest(
        timestamp=20.0,
        stream_id="stream_sintel",
        user_query="Catch me up on the story so far (spoiler-free recap)",
    )
    res = engine.analyze_frame_and_query(req)
    assert len(res.trivia_cards) >= 1
    assert any(c.category == "recap" for c in res.trivia_cards), f"Expected recap card, got {[c.category for c in res.trivia_cards]}"
