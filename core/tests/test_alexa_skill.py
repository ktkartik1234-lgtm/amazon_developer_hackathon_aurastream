"""
Automated Test Suite for Amazon Alexa Skills Kit (ASK v1.0) & Alexa+ Webhook Integration.
"""

from fastapi.testclient import TestClient
from core.app.main import app

client = TestClient(app)


def test_alexa_skill_manifest_endpoint():
    res = client.get("/api/alexa/skill-manifest")
    assert res.status_code == 200
    data = res.json()
    assert "manifest" in data
    assert data["manifest"]["publishingInformation"]["locales"]["en-US"]["name"] == "AuraStream"


def test_alexa_interaction_model_endpoint():
    res = client.get("/api/alexa/interaction-model")
    assert res.status_code == 200
    data = res.json()
    lm = data["interactionModel"]["languageModel"]
    assert lm["invocationName"] == "aura stream"
    intent_names = {i["name"] for i in lm["intents"]}
    assert "AskSceneIntent" in intent_names
    assert "SpoilerFreeRecapIntent" in intent_names
    assert "WhatSongIntent" in intent_names


def test_alexa_webhook_launch_request():
    envelope = {
        "version": "1.0",
        "session": {"new": True, "sessionId": "amzn1.echo-api.session.test", "attributes": {}},
        "request": {"type": "LaunchRequest", "requestId": "amzn1.echo-api.request.1"},
    }
    res = client.post("/api/alexa/webhook", json=envelope)
    assert res.status_code == 200
    body = res.json()
    assert body["version"] == "1.0"
    speech = body["response"]["outputSpeech"]
    assert speech["type"] == "SSML"
    assert "<speak>" in speech["ssml"]
    assert "Welcome to AuraStream on Fire TV" in speech["text"]
    assert body["response"]["directives"][0]["type"] == "Alexa.Presentation.APL.RenderDocument"


def test_alexa_webhook_ask_scene_intent_brass_compass():
    envelope = {
        "version": "1.0",
        "session": {"new": False, "attributes": {"stream_id": "stream_sintel", "timestamp": 42.0}},
        "request": {
            "type": "IntentRequest",
            "intent": {
                "name": "AskSceneIntent",
                "slots": {"query": {"name": "query", "value": "what did he just drop"}},
            },
        },
    }
    res = client.post("/api/alexa/webhook", json=envelope)
    assert res.status_code == 200
    body = res.json()
    assert "brass compass" in body["response"]["outputSpeech"]["text"].lower()
    assert body["aurastream_meta"]["spoiler_shield_timestamp"] == 42.0


def test_alexa_webhook_pause_intent_dispatches_to_fire_tv_bus():
    envelope = {
        "version": "1.0",
        "session": {"new": False, "attributes": {}},
        "request": {
            "type": "IntentRequest",
            "intent": {"name": "AMAZON.PauseIntent"},
        },
    }
    res = client.post("/api/alexa/webhook", json=envelope)
    assert res.status_code == 200
    body = res.json()
    cmd_ev = body["aurastream_meta"]["command_dispatched"]
    assert cmd_ev["command"] == "pause"
    assert cmd_ev["source"] == "alexa_plus_skill"


def test_alexa_webhook_direct_utterance():
    res = client.post(
        "/api/alexa/webhook",
        json={"utterance": "Wait, what did he just drop?", "stream_id": "stream_sintel", "timestamp": 42.0},
    )
    assert res.status_code == 200
    body = res.json()
    assert "brass compass" in body["response"]["outputSpeech"]["text"].lower()
