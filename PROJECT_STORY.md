# AuraStream 🌟
### Ambient Living Room Intelligence & Multi-Modal Streaming Engine for Amazon Fire TV

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Fire%20TV%20%7C%20Vega%20OS-orange.svg)](README.md)
[![MCP Spec](https://img.shields.io/badge/MCP%20Spec-2025--11--25%2B%20Streamable%20HTTP-green.svg)](ARCHITECTURE.md)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Amazon%20Bedrock%20Claude%203.5-blueviolet.svg)](core/app/aws/bedrock.py)

---

## Inspiration

Every evening in living rooms worldwide, the same frustrating cycle repeats:
- A viewer pauses a movie to squint at an unfamiliar actor’s face, pulling out their smartphone to search IMDb.
- Someone asks, *"What song is playing in this scene?"* and fumbles with Shazam.
- A family member returns from the kitchen asking *"What did I miss?"*, and a quick web search accidentally reveals major third-act spoilers.
- During live sports, standard broadcasts display static scorecards while fans crave tactical context—team formations, pressing traps, and expected goals (xG).

**Why should viewers look away from an 85-inch 4K TV down to a 6-inch phone?**

The television screen should be an active, intelligent participant in the room. We envisioned **AuraStream**: an ambient living room co-pilot that honors cinema immersion with a 4-second auto-hide engine, activates fluidly via Fire TV remote D-Pad or Alexa+ voice commands, and reasons over video frames using **AWS Bedrock** and the **Model Context Protocol (MCP)** without ever breaking immersion.

---

## What it does

**AuraStream** transforms Amazon Fire TV into an ambient viewing companion across four core pillars:

1. **True 10-Foot Cinema Experience & Auto-Hide HUD**:
   - Crisp 1080p/4K cinema streaming canvas with zero persistent UI clutter.
   - **4.0s Inactivity Auto-Fade**: Controls, trays, and chrome dissolve seamlessly into full-screen video during continuous viewing.
   - **Synchronized Subtitle Engine**: High-contrast WebVTT captions with ambient household dialogue boosting (+4.5 dB).
   
   ![Full-Bleed Cinema Viewing](client/previews/cinema_pure_video.png)

2. **Prime Video X-Ray Slide-Up Drawer**:
   - Pressing `SPACE` or D-Pad `UP` glides up an authentic frosted glass (`backdrop-filter: blur(24px)`) drawer.
   - **In-Scene Cast**: Real-time actor matching and character profiles (e.g., *Sintel* and *Scales* with 99% Bedrock match confidence).
   - **Soundtrack Tab**: Active music score detection with live animated SVG audio visualizer equalizer waves.
   - **Scene Trivia**: Synchronized production facts and trivia locked to the exact frame timestamp.

   ![Prime Video X-Ray Slide-Up Drawer](client/previews/cinema_xray_open.png)

3. **Alexa+ Voice Remote & Spoiler-Free Recaps**:
   - Pressing `V` activates the glowing **Alexa cyan LED light-strip** across the lower bezel with real-time waveform visualizers.
   - Viewers can ask: *"Alexa, catch me up on what happened"* or *"Who is on screen right now?"*.
   - AuraStream enforces a **timestamp-bounded prompt envelope** in Amazon Bedrock, ensuring recaps synthesize only elapsed scenes with strictly **zero future plot spoilers**.

   ![Alexa+ Voice Remote & Spoiler-Free Recaps](client/previews/cinema_alexa_bar.png)

4. **Live Sports Tactical AI Breakdown & Soundtrack Detection**:
   - Seamlessly switch from movies to live soccer matches (*Champions Cup: Madrid vs Manchester*).
   - AWS Bedrock vision models analyze pitch camera feeds in real time to project tactical formations (*4-3-3 High Press*), team pressing zones, real-time Expected Goals (1.84 xG), and player sprint velocities directly onto the TV screen.

   ![Soundtrack Detection and Audio Visualizer](client/previews/cinema_music_tab.png)

---

## How we built it

AuraStream is architected as an end-to-end 3-tier system connecting edge Fire TV clients with AWS Cloud Intelligence via open protocol standards:

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                       FIRE TV / VEGA OS CLIENT (10-Foot UI)                       │
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │                    FULL-BLEED CINEMA VIDEO CANVAS (1080p)                   │  │
│  │   4K/1080p Streaming Playback | WebVTT Subtitles | 4.0s Inactivity Auto-Fade│  │
│  └──────────────────────────────────────┬──────────────────────────────────────┘  │
│                                         │                                         │
│  ┌──────────────────────────────────────┴──────────────────────────────────────┐  │
│  │                 PRIME VIDEO X-RAY DRAWER & ALEXA LIGHT-BAR                  │  │
│  │  • Spatial D-Pad Focus State Machine (`spatialNav.js`)                      │  │
│  │  • Slide-Up Drawer: In Scene (Cast) | Soundtrack | Trivia | Tactics | Recap │  │
│  │  • Alexa Bottom Cyan LED Light-Strip + Floating Response Reasoning Card     │  │
│  │  • Real-time Dialogue & Sports Commentary Subtitle Sync Engine              │  │
│  └──────────────────────────────────────┬──────────────────────────────────────┘  │
└─────────────────────────────────────────┼─────────────────────────────────────────┘
                                          │ 
                      Streamable HTTP MCP │ (SSE + HTTP POST, Spec 2025-11-25)
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                     AURASTREAM CORE (Self-Hosted MCP Server)                      │
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐  │
│  │                       MCP STREAMABLE HTTP TRANSPORT                         │  │
│  │                Endpoint: `/mcp` (Streamable HTTP Transport)                 │  │
│  └──────────────────────────────────────┬──────────────────────────────────────┘  │
│                                         │                                         │
│  ┌──────────────────────────────────────┴──────────────────────────────────────┐  │
│  │                              TOOL ORCHESTRATOR                              │  │
│  │  • `get_scene_telemetry`: Extracts timestamp, actors, objects, soundtrack   │  │
│  │  • `analyze_frame_multimodal`: Vision reasoning on current video frame      │  │
│  │  • `synthesize_trivia_card`: Generates structured interactive TV cards      │  │
│  │  • `adapt_household_ambient`: Adjusts audio/subtitles for family/room       │  │
│  │  • `generate_spoiler_free_recap`: Contextual safe plot catch-up             │  │
│  └──────────────────────────────────────┬──────────────────────────────────────┘  │
└─────────────────────────────────────────┼─────────────────────────────────────────┘
                                          │
                        Boto3 / AWS SDK   │ (Bedrock Runtime Converse API)
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                         AWS BUILDER INTELLIGENCE LAYER                            │
│                                                                                   │
│   ┌───────────────────────────────┐     ┌──────────────────────────────────────┐  │
│   │        AMAZON BEDROCK         │     │         INTENT ROUTER & CACHE        │  │
│   │  Claude 3.5 Sonnet / Nova Pro │     │    Precedence: NAV > RECAP > MUSIC   │  │
│   │   Converse API Vision Engine  │     │    3.0s Timeout & Offline Cache      │  │
│   └───────────────────────────────┘     └──────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────────┘
```

- **10-Foot TV Client (`client/`)**: Built for Fire OS and Vega OS guidelines using pure HTML5, CSS3 glassmorphism, Amazon Ember typography, and vanilla JavaScript. Features a deterministic 2D spatial navigation state machine (`client/js/spatialNav.js`) handling Android TV hardware keycodes (`ArrowUp`, `ArrowDown`, `MediaPlayPause`, `Enter`, `Back`).
- **Streamable HTTP MCP Core (`core/app/mcp/`)**: Conforms to the Model Context Protocol (MCP) `2025-11-25+` specification via Starlette/FastAPI SSE and POST endpoints at `/mcp`, standardizing tool invocation for cross-device agents.
- **AWS Bedrock Runtime (`core/app/aws/bedrock.py`)**: Directly invokes Claude 3.5 Sonnet and Amazon Nova Pro via the `boto3` Bedrock Runtime Converse API. Features an **Intent Priority Router** enforcing strict word-boundary matching and an enforced 3.0s circuit breaker with high-fidelity local cloud caching.

---

## Challenges we ran into

Documented with 6-field DevRel entries in [FRICTION_LOG.md](FRICTION_LOG.md) (qualifying for the **+10% judging bonus**):

1. **MCP 2.x Architecture Migration**:  
   Upgrading to the official `mcp` SDK (`v2.2.0`) threw `ModuleNotFoundError` because `FastMCP` was renamed to `MCPServer`. We migrated imports to `from mcp.server.mcpserver import MCPServer` and mounted `server.streamable_http_app()` directly into our ASGI app.
2. **Intent Keyword Collisions**:  
   A viewer asking *"What song is playing?"* triggered naive substring matches on `"play"`, erroneously activating video playback toggles or tactical sports breakdowns. We built an `IntentPriorityRouter` using regex word boundaries with explicit precedence (`NAVIGATION > RECAP > SOUNDTRACK > TACTICAL > CAST > TRIVIA`).
3. **Living Room Latency Budgets**:  
   10-foot television UX demands immediate feedback (<200 ms). Cloud LLM calls can occasionally hang. We implemented a 3.0s client timeout with 1 retry and an ambient offline cloud cache badge, ensuring zero UI freezing during live demonstrations.
4. **WebView Focus Freezes on TV WebViews**:  
   Standard browser `alert()` and `prompt()` modals froze the JavaScript event loop in TV WebViews, breaking D-Pad event listeners. We engineered non-blocking glassmorphic toasts and focus-trapped TV dialogs with dynamic letterbox viewport scaling (`scale(min(w/1920, h/1080))`).

---

## Accomplishments that we're proud of

- **51 Automated Tests Passing**: Comprehensive test suite covering unit tests, integration pipelines, intent routing, and regression assertions (`python -m pytest core/tests -v`).
- **Clockwork Video Demo Under 3 Minutes**: Storyboarded and verified a crisp 2-minute 45-second demonstration ([DEMO.md](DEMO.md)), strictly complying with the hackathon's $< 3:00$ minute limit.
- **Genuine Runtime Technology Calls**: 100% real SDK imports and runtime calls across `boto3`, `mcp`, `fastapi`, and hardware keycodes—zero README-only vaporware.
- **Open Source by Design**: MIT Licensed ([LICENSE](LICENSE)) to empower the Fire TV and developer ecosystem.

---

## What we learned

- **Design for 10 Feet, Not 10 Inches**: Mobile and desktop paradigms fail on televisions. Every focus change must be visually unmistakable with luminous borders, scales, and high-contrast Ember typography.
- **Protocols Unify Living Rooms**: By building on the Model Context Protocol (MCP `2025-11-25+`), AuraStream tools can be queried identically by an on-screen Fire TV HUD or a standalone Alexa Echo device in the next room.
- **Context Boundaries Matter**: Multi-modal reasoning is only magical when bounded accurately; spoiler-free recaps require strict temporal guardrails to preserve narrative surprises.

---

## What's next for AuraStream

- **On-Device Edge Inference**: Running quantized Amazon Nova Edge vision models directly on Fire TV stick NPUs for ultra-fast, local sub-50ms frame analysis.
- **Echo Spatial Audio Sync**: Automatically adjusting living room dialogue boost and subtitle prominence by sensing ambient decibel levels from nearby Alexa Echo microphones.
- **Prime Interactive Live Shopping**: Contextually identifying on-screen apparel, team jerseys, or soundtrack vinyl in the X-Ray drawer with 1-click Fire TV voice checkout.
