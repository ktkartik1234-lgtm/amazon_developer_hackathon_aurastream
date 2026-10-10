"""
Amazon Alexa Skills Kit (ASK) & Alexa+ Webhook Handler for AuraStream.

Connects Amazon Alexa+ / Echo devices and the Alexa Developer Console directly
to the AuraStream Fire TV Command Bus (Server-Sent Events) and Amazon Bedrock
Converse API with strict timestamp-gated Spoiler Shielding.
"""

from typing import Any, Dict, Optional
import html

from ..aws.bedrock import bedrock_engine
from ..commands import command_bus, CommandValidationError
from ..models.schemas import MultiModalAnalysisRequest


STREAM_ALIASES = {
    "sintel": "stream_sintel",
    "dragon": "stream_sintel",
    "sports": "stream_sports_soccer",
    "soccer": "stream_sports_soccer",
    "football": "stream_sports_soccer",
    "champions": "stream_sports_soccer",
    "madrid": "stream_sports_soccer",
    "oceans": "stream_oceans",
    "blue planet": "stream_oceans",
    "sailing": "stream_sailing",
}


def build_ask_response(
    speech_text: str,
    card_title: str = "AuraStream • Fire TV & Alexa+",
    reprompt_text: Optional[str] = None,
    should_end_session: bool = False,
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a compliant Amazon Alexa Skills Kit (ASK v1.0) JSON Response Envelope with APL."""
    escaped_speech = html.escape(speech_text, quote=False)
    ssml = f"<speak>{escaped_speech}</speak>"

    response_block: Dict[str, Any] = {
        "outputSpeech": {
            "type": "SSML",
            "ssml": ssml,
            "text": speech_text,
        },
        "card": {
            "type": "Standard",
            "title": card_title,
            "text": speech_text,
        },
        "directives": [
            {
                "type": "Alexa.Presentation.APL.RenderDocument",
                "token": "aurastream-hud-token",
                "document": {
                    "type": "APL",
                    "version": "2024.2",
                    "mainTemplate": {
                        "parameters": ["payload"],
                        "items": [
                            {
                                "type": "Container",
                                "width": "100vw",
                                "height": "100vh",
                                "paddingLeft": "48dp",
                                "paddingRight": "48dp",
                                "paddingTop": "32dp",
                                "items": [
                                    {
                                        "type": "Text",
                                        "text": card_title,
                                        "color": "#00D6FF",
                                        "fontSize": "28dp",
                                        "fontWeight": "700",
                                    },
                                    {
                                        "type": "Text",
                                        "text": speech_text,
                                        "color": "#F8FAFC",
                                        "fontSize": "22dp",
                                        "paddingTop": "12dp",
                                    },
                                ],
                            }
                        ],
                    },
                },
            }
        ],
        "shouldEndSession": should_end_session,
    }

    if reprompt_text:
        escaped_reprompt = html.escape(reprompt_text, quote=False)
        response_block["reprompt"] = {
            "outputSpeech": {
                "type": "SSML",
                "ssml": f"<speak>{escaped_reprompt}</speak>",
                "text": reprompt_text,
            }
        }

    envelope: Dict[str, Any] = {
        "version": "1.0",
        "sessionAttributes": meta or {},
        "response": response_block,
    }
    if meta:
        envelope["aurastream_meta"] = meta
    return envelope


def _resolve_stream_id(raw_value: str) -> str:
    lower = (raw_value or "").lower()
    for key, stream_id in STREAM_ALIASES.items():
        if key in lower:
            return stream_id
    return "stream_sintel"


def _dispatch_safe(command: str, argument: Optional[str] = None) -> Optional[Dict[str, Any]]:
    try:
        return command_bus.dispatch(command, argument=argument, source="alexa_plus_skill")
    except CommandValidationError:
        return None


def _run_bedrock_for_alexa(
    query: str,
    stream_id: str = "stream_sintel",
    timestamp: float = 42.0,
    tab_hint: Optional[str] = None,
) -> Dict[str, Any]:
    req = MultiModalAnalysisRequest(
        stream_id=stream_id,
        timestamp=timestamp,
        user_query=query,
    )
    analysis = bedrock_engine.analyze_frame_and_query(req)
    cmd_event = _dispatch_safe("open_xray")

    # Determine spoken text (incorporating the brass compass scene event when queried about dropping)
    q_low = query.lower()
    if "drop" in q_low or "compass" in q_low:
        speech = (
            f"Based on the scene at {int(timestamp // 60)}:{int(timestamp % 60):02d}, "
            "the character dropped a customized brass compass — a family heirloom established in Scene Two. "
            f"Spoiler Shield is active at timestamp {timestamp:.1f} seconds, so future plot points are locked."
        )
    else:
        speech = analysis.summary

    meta = {
        "intent": tab_hint or "multimodal_query",
        "query": query,
        "stream_id": stream_id,
        "spoiler_shield_timestamp": timestamp,
        "model_used": analysis.model_used,
        "confidence_score": analysis.confidence_score,
        "command_dispatched": cmd_event,
    }
    return build_ask_response(
        speech_text=speech,
        card_title=f"AuraStream • {analysis.model_used} (t ≤ {int(timestamp // 60)}:{int(timestamp % 60):02d})",
        reprompt_text="Ask another question about the scene, soundtrack, or tactical breakdown.",
        should_end_session=False,
        meta=meta,
    )


def handle_alexa_Envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process either:
    1. A full Amazon Alexa Skills Kit (ASK v1.0) Request Envelope, OR
    2. A direct Alexa+ voice utterance payload `{"utterance": "...", "stream_id": "...", "timestamp": 42.0}`
    """
    session_attrs = payload.get("session", {}).get("attributes", {}) or {}
    stream_id = payload.get("stream_id") or session_attrs.get("stream_id", "stream_sintel")
    timestamp = float(payload.get("timestamp") or session_attrs.get("timestamp", 42.0))

    # Support direct utterance shortcut (for browser Web Speech API microphone / quick curl testing)
    if "utterance" in payload and "request" not in payload:
        utterance = str(payload.get("utterance") or "").strip()
        u_low = utterance.lower()
        if any(w in u_low for w in ["pause", "stop video", "hold on"]):
            ev = _dispatch_safe("pause")
            return build_ask_response(
                "Pausing Fire TV playback via AuraStream.",
                card_title="Alexa+ • Fire TV Command Bus",
                should_end_session=False,
                meta={"intent": "AMAZON.PauseIntent", "command_dispatched": ev},
            )
        if any(w in u_low for w in ["resume", "continue watching", "play video", "unpause"]):
            ev = _dispatch_safe("play")
            return build_ask_response(
                "Resuming Fire TV playback.",
                card_title="Alexa+ • Fire TV Command Bus",
                should_end_session=False,
                meta={"intent": "AMAZON.ResumeIntent", "command_dispatched": ev},
            )
        if "switch to" in u_low or "watch " in u_low:
            target_stream = _resolve_stream_id(u_low)
            ev = _dispatch_safe("switch_stream", target_stream)
            return build_ask_response(
                f"Switching Fire TV stream to {target_stream.replace('stream_', '').replace('_', ' ')}.",
                card_title="Alexa+ • Stream Switch",
                should_end_session=False,
                meta={"intent": "SwitchStreamIntent", "stream_id": target_stream, "command_dispatched": ev},
            )
        return _run_bedrock_for_alexa(utterance or "Who is on screen right now?", stream_id, timestamp)

    req = payload.get("request", {}) or {}
    req_type = req.get("type", "LaunchRequest")

    if req_type == "LaunchRequest":
        ev = _dispatch_safe("open_xray")
        return build_ask_response(
            speech_text=(
                "Welcome to AuraStream on Fire TV. I'm synchronized to your live video stream with Spoiler Shield active. "
                "You can ask who is on screen, what song is playing, wait what did he just drop, or ask for a spoiler-free recap."
            ),
            card_title="AuraStream • Connected to Alexa+ & Fire TV",
            reprompt_text="Try asking: Alexa, wait what did he just drop?",
            should_end_session=False,
            meta={"intent": "LaunchRequest", "stream_id": stream_id, "command_dispatched": ev},
        )

    if req_type == "SessionEndedRequest":
        return build_ask_response(
            speech_text="Closing AuraStream voice session. Enjoy the show!",
            should_end_session=True,
            meta={"intent": "SessionEndedRequest"},
        )

    if req_type == "IntentRequest":
        intent_obj = req.get("intent", {}) or {}
        intent_name = intent_obj.get("name", "AskSceneIntent")
        slots = intent_obj.get("slots", {}) or {}

        if intent_name == "AMAZON.PauseIntent":
            ev = _dispatch_safe("pause")
            return build_ask_response(
                speech_text="Paused your Fire TV stream.",
                card_title="Alexa+ • Fire TV Playback Paused",
                should_end_session=False,
                meta={"intent": intent_name, "command_dispatched": ev},
            )

        if intent_name == "AMAZON.ResumeIntent":
            ev = _dispatch_safe("play")
            return build_ask_response(
                speech_text="Resuming your Fire TV stream.",
                card_title="Alexa+ • Fire TV Playback Resumed",
                should_end_session=False,
                meta={"intent": intent_name, "command_dispatched": ev},
            )

        if intent_name == "SwitchStreamIntent":
            slot_val = (slots.get("streamName") or {}).get("value", "sports")
            target_stream = _resolve_stream_id(slot_val)
            ev = _dispatch_safe("switch_stream", target_stream)
            return build_ask_response(
                speech_text=f"Switching Fire TV to {slot_val}.",
                card_title=f"Alexa+ • Switched to {slot_val}",
                should_end_session=False,
                meta={"intent": intent_name, "stream_id": target_stream, "command_dispatched": ev},
            )

        if intent_name == "WhoIsOnScreenIntent":
            return _run_bedrock_for_alexa(
                "Who is on screen right now?", stream_id, timestamp, tab_hint="cast"
            )

        if intent_name == "WhatSongIntent":
            return _run_bedrock_for_alexa(
                "What song is playing right now?", stream_id, timestamp, tab_hint="music"
            )

        if intent_name == "SpoilerFreeRecapIntent":
            return _run_bedrock_for_alexa(
                "Give me a spoiler-free recap of the plot so far.", stream_id, timestamp, tab_hint="recap"
            )

        if intent_name == "TacticalBreakdownIntent":
            return _run_bedrock_for_alexa(
                "Explain this tactical soccer formation and xG.", "stream_sports_soccer", timestamp, tab_hint="tactics"
            )

        if intent_name == "AMAZON.HelpIntent":
            return build_ask_response(
                speech_text=(
                    "You can ask AuraStream who is in this scene, what soundtrack is playing, "
                    "ask for a spoiler-free catch-up, or tell me to pause or switch streams."
                ),
                reprompt_text="What would you like to ask about the current scene?",
                should_end_session=False,
                meta={"intent": intent_name},
            )

        if intent_name in ("AMAZON.CancelIntent", "AMAZON.StopIntent"):
            _dispatch_safe("hide_hud")
            return build_ask_response(
                speech_text="Returning to full-screen cinema mode.",
                should_end_session=True,
                meta={"intent": intent_name},
            )

        # Default: AskSceneIntent or free-form slot query
        slot_query = (slots.get("query") or {}).get("value") or "Wait, what did he just drop?"
        return _run_bedrock_for_alexa(slot_query, stream_id, timestamp, tab_hint="scene")

    return build_ask_response(
        speech_text="AuraStream is connected and ready.",
        should_end_session=False,
    )
