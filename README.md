# AuraStream 🌟
### Ambient Living Room Intelligence & Multi-Modal Streaming Engine for Amazon Fire TV

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Fire%20TV%20%7C%20Vega%20OS-orange.svg)]()
[![MCP Spec](https://img.shields.io/badge/MCP%20Spec-2025--11--25%2B%20Streamable%20HTTP-green.svg)]()
[![AWS Bedrock](https://img.shields.io/badge/AWS-Amazon%20Bedrock%20Claude%203.5-blueviolet.svg)]()

> **Amazon Developer Hackathon Submission**  
> **Primary Track**: Fire TV (Priority Categories: *AI-Enhanced Viewing*, *Multi-Modal UX*, *Sports & Entertainment*)  
> **Mini-Challenges**: AWS Builder (Amazon Bedrock Multi-Modal) & Open Source (MIT Licensed)  
> **Bonus**: Verified Friction Log (+10% Judging Bonus in `FRICTION_LOG.md`)

---

## 1. Project Overview & Customer Value

Traditional streaming interfaces treat the television as a passive display. Viewers constantly reach for their smartphones to look up actors, pause to search for song names, or miss tactical play context during live sports broadcasts.

**AuraStream** transforms the Fire TV experience into an **intelligent, ambient living room companion**:
- **Continuous Scene Comprehension**: Automatically tracks characters on screen, objects, background music, and production trivia synchronized to exact video timestamps.
- **Multi-Modal AI Co-Pilot**: Combines Fire TV remote D-Pad spatial navigation, Alexa+ voice queries, and glassmorphism HUD overlays into a single, cohesive 10-foot living room flow.
- **Deep AWS Bedrock Reasoning**: Leverages **Amazon Bedrock (Claude 3.5 Sonnet / Nova Pro)** to perform zero-lag visual frame analysis, real-time sports tactical breakdowns, and spoiler-free storyline recaps.
- **Standardized MCP 2025-11-25+ Streamable HTTP Core**: Powered by an underlying Model Context Protocol (MCP) server exposing native living room tools for cross-device orchestration between Fire TV and Alexa+.

---

## 2. System Architecture

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                       FIRE TV / VEGA OS CLIENT (10-Foot UI)                       │
│                                                                                   │
│  ┌───────────────────────────────────────┬─────────────────────────────────────┐  │
│  │         HERO VIDEO CANVAS             │          AURA PULSE HUD             │  │
│  │     60 FPS Streaming Viewport         │    Live Cast | Music | Trivia       │  │
│  └───────────────────────────────────────┴─────────────────────────────────────┘  │
│                                    ▲                                              │
│                        SpatialNav  │ (D-Pad Codes: 37-40, 19-23, Select, Back)   │
│                                    ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │       CONTEXTUAL QUICK-ACTION PILLS & INTERACTIVE GLASSMORPHISM CARDS       │  │
│  │   "Who is on screen?" | "Explain tactics" | "Soundtrack" | "Family Adapt"   │  │
│  └──────────────────────────────────────┬──────────────────────────────────────┘  │
└─────────────────────────────────────────┼─────────────────────────────────────────┘
                                          │ 
                      Streamable HTTP MCP │ (SSE + HTTP POST, Spec 2025-11-25)
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                     AURASTREAM CORE (Self-Hosted MCP Server)                      │
│                                                                                   │
│  • `get_scene_telemetry(timestamp, stream_id)`                                    │
│  • `analyze_frame_multimodal(timestamp, user_query, image_base64)`                │
│  • `adapt_household_ambient(viewer_profile, ambient_noise_level)`                 │
│  • `generate_spoiler_free_recap(current_time, stream_id)`                         │
└─────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │
                        Boto3 / AWS SDK   │ (Bedrock Runtime)
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                   AWS BEDROCK & MULTI-MODAL REASONING LAYER                       │
│                                                                                   │
│  • Claude 3.5 Sonnet & Amazon Nova Pro Vision Analysis                            │
│  • Unified Boto3 Converse API Integration                                         │
│  • Verified Fallback Engine for Zero-Lag Offline Evaluation                       │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Quickstart & Local Execution

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Modern web browser (Chrome, Edge, Firefox) or Fire TV / Vega OS Simulator

### Step 1: Install Dependencies
```bash
cd amazon_developer_hackathon_aurastream
pip install fastapi uvicorn pydantic mcp boto3 botocore sse-starlette httpx pytest
```

### Step 2: Run Automated Test Suite
Verify that all 50 unit, integration, intent router, and regression tests pass:
```bash
python -m pytest core/tests -v
```

### Step 3: Launch AuraStream Server & Fire TV Client
Launch via the zero-friction runner:
```bash
python run.py
```
*(Alternatively: `python -m uvicorn core.app.main:app --app-dir . --host 127.0.0.1 --port 8000 --reload`)*

### Step 4: Open Fire TV 10-Foot Experience
Open your browser or Fire TV WebView simulator to:
**`http://localhost:8000/`**

---

## 4. 10-Foot Remote Controls & Navigation Legend

| Remote Action | Keyboard Key | Android TV Keycode | Function |
| :--- | :--- | :--- | :--- |
| **D-Pad Left / Right** | `ArrowLeft` / `ArrowRight` | `21` / `22` | Navigate between Action Pills or Insight Cards |
| **D-Pad Up / Down** | `ArrowUp` / `ArrowDown` | `19` / `20` | Move focus between Action Pills and Card Carousel |
| **Select / Center** | `Enter` | `13` / `23` / `66` | Activate selected pill or view detailed card |
| **Back Button** | `Escape` / `Backspace` | `4` / `27` | Dismiss open cards overlay |
| **Alexa Voice Trigger** | `V` | Key `V` | Simulate Alexa+ push-to-talk speech query |

---

## 5. Amazon Developer Hackathon Compliance Checklist

- [x] **Primary Track**: Fire TV (works cleanly in Fire TV / Vega simulator and TV WebView).
- [x] **Mini-Challenge 1 (AWS Builder)**: Direct Amazon Bedrock Converse API multi-modal integration in `core/app/aws/bedrock.py`.
- [x] **Mini-Challenge 2 (Open Source)**: Standalone MIT Open Source License in `LICENSE`.
- [x] **MCP Spec Compliance**: Conforms to MCP Specification `2025-11-25+` via Streamable HTTP transport mounted at `/mcp`.
- [x] **Runtime Technology Calls**: Real imports and runtime execution of `boto3`, `mcp`, `fastapi`, and spatial navigation events.
- [x] **Friction Log Bonus**: Documented first-party feedback and friction logs in `FRICTION_LOG.md` (up to **+10% judging bonus**).
- [x] **Demo Video Limit**: Designed for a concise 2-minute 45-second high-impact demonstration (< 3:00 minutes).

---

## 6. Judges & Collaborator Access Guide

If accessing this repository privately, the following Amazon Developer Relations team members must be invited per the official hackathon rules:
- `chris-trag` (Chris Traganos)
- `knmeiss` (Kourtney Meiss)
- `giolaq` (Giovanni Laquidara)
- `anishamalde` (Anisha Malde)
- `mosesroth` (Moses Roth)
- `emersonsklar` (Emerson Sklar)
- `testing@devpost.com`
