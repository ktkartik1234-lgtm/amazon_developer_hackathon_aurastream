"""
Adversarial and comprehensive regression tests for AuraStream Intent Priority Router.
Validates zero keyword collisions, intent disambiguation, and edge-case query phrasings.
"""

import pytest
from core.app.aws.bedrock import classify_user_intent, IntentType


@pytest.mark.parametrize(
    "query,expected_intent",
    [
        # Soundtrack intent (Disambiguated from "play")
        ("What soundtrack is playing right now?", IntentType.SOUNDTRACK),
        ("What song is playing?", IntentType.SOUNDTRACK),
        ("Who is the composer of this orchestral score?", IntentType.SOUNDTRACK),
        ("What music track is this?", IntentType.SOUNDTRACK),
        # Navigation intent (Disambiguated from "play")
        ("Can I play the video now?", IntentType.NAVIGATION),
        ("Pause video playback please", IntentType.NAVIGATION),
        ("Resume playback", IntentType.NAVIGATION),
        ("Fast forward 10 seconds", IntentType.NAVIGATION),
        # Recap / Catch-up intent
        ("Catch me up on the storyline so far", IntentType.RECAP),
        ("Give me a spoiler-free recap", IntentType.RECAP),
        ("What has happened in the plot so far?", IntentType.RECAP),
        ("Catch up summary", IntentType.RECAP),
        # Tactical / Sports intent
        ("Explain this tactical soccer formation", IntentType.TACTICAL),
        ("What tactics is Madrid using in this counter-attack?", IntentType.TACTICAL),
        ("What is the current possession and xG?", IntentType.TACTICAL),
        ("Show me the playbook strategy", IntentType.TACTICAL),
        # Cast / Character intent
        ("Who is on screen right now?", IntentType.CAST),
        ("Who's the main actor in this scene?", IntentType.CAST),
        ("Which character is speaking?", IntentType.CAST),
        ("Who stars in Sintel?", IntentType.CAST),
        # Trivia / Production intent
        ("What is some behind the scenes trivia?", IntentType.TRIVIA),
        ("Who directed this movie?", IntentType.TRIVIA),
        ("Tell me about the open source blender pipeline", IntentType.TRIVIA),
    ],
)
def test_adversarial_intent_classification(query, expected_intent):
    actual_intent = classify_user_intent(query)
    assert actual_intent == expected_intent, f"Query '{query}' classified as {actual_intent}, expected {expected_intent}"
