# AuraStream System Architecture & Technical Specification

**System Name**: AuraStream  
**Target Platform**: Amazon Fire TV (Fire OS / Vega OS)  
**Protocol Standards**: Model Context Protocol (MCP) Spec 2025-11-25+ (Streamable HTTP)  
**Cloud AI Services**: Amazon Bedrock (Multi-Modal Vision & Reasoning), AWS AgentCore  
**License**: MIT License (Open Source Mini-Challenge)

---

## 1. High-Level Architecture Diagram

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
│  │  • `adapt_household_ambient`: Adjusts audio/subtitles for family/room       │  │
│  │  • `generate_spoiler_free_recap`: Contextual safe plot catch-up             │  │
│  │  • `dispatch_fire_tv_command`: Alexa+ drives the TV (SSE command bus)       │  │
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

---

## 2. Component Specifications

### 2.1 Tier 1: Client Application (`client/`)
- **Technology**: TV Web / React Native TV compatible, conforming to Vega OS and Fire OS TV guidelines.
- **Focus Management**: Implements strict 10-foot spatial navigation (`spatialNav.js`). Key events:
  - `ArrowLeft` / `ArrowRight` (Codes 21, 22): Navigate between X-Ray tabs or carousel cards.
  - `ArrowUp` / `ArrowDown` (Codes 19, 20): Traverse between Drawer Tabs and Content Tray cards.
  - `Space` / `k` / `MediaPlayPause` (Codes 85, 179): Toggle playback and open/close Prime Video X-Ray drawer.
  - `Enter` / `Select` (Codes 13, 23, 66): Trigger action / switch stream catalog item.
  - `Escape` / `Backspace` / `Back` (Codes 4, 27): Dismiss drawer / Alexa card back to 100% full-bleed video.
  - `KeyV` (Voice Trigger): Activate Alexa bottom glowing cyan LED light-strip.
  - `KeyC` (CC Subtitles): Toggle synchronized dialogue and sports commentary subtitles.
  - `]` / `[` (Codes 221, 219): Seek 10s forward / backward (remote fast-forward / rewind).
  - `KeyR` (Restart): Reset playback to the beginning of the stream.
  - `KeyA` (Ambient): Apply Adaptive Ambient Household Mode via `/api/ambient-adapt`.
- **Command Bus Subscriber**: `mcpClient.js` consumes the Fire TV command bus (`GET /api/events`, Server-Sent Events) so Alexa+ and MCP tool callers drive playback live (play, pause, seek, switch_stream, ...).
- **Visual Design**: Cinema-grade Prime Video aesthetic with Amazon Ember typography, frosted glass (`backdrop-filter: blur(24px)`), cyan glowing focus borders, and zero-clutter 4-second auto-hide fade.

### 2.2 Tier 2: Streamable HTTP MCP Server (`core/app/mcp/`)
- **Protocol**: Model Context Protocol (MCP) Streamable HTTP Transport (Specification Version: `2025-11-25+`).
- **Endpoints**:
  - `GET /mcp`: Server-Sent Events stream for real-time notifications and responses.
  - `POST /mcp`: JSON-RPC 2.0 message handler for client initialization, tool execution, and ping requests.
  - `GET /health`: Health check and system readiness probe.
  - `GET /api/telemetry`: Canonical time-coded telemetry for all video streams.
  - `POST /api/multimodal-query`: Intent Priority Router query interface with Bedrock Converse execution.
  - `POST /api/ambient-adapt`: Household ambient adaptation (dialogue boost, subtitle sizing, rating cap).
  - `POST /api/remote-command`: Fire TV Command Bus dispatch (Alexa+ / MCP drives the TV).
  - `GET /api/events`: Server-Sent Events stream of Fire TV commands with Last-Event-ID resume.
- **Schemas**: Strict Pydantic v2 schemas validating all inputs, responses, and tool arguments.

### 2.3 Tier 3: AWS Builder Services (`core/app/aws/`)
- **Service Integration**: Amazon Bedrock Runtime (`bedrock-runtime`).
- **Models**:
  - `anthropic.claude-3-5-sonnet-20241022-v2:0` or `amazon.nova-pro-v1:0` for multi-modal vision and natural conversation.
- **Resilience Strategy**:
  - Primary path: Direct call to AWS Bedrock Runtime Converse API when credentials are authenticated.
  - Circuit Breaker: 3.0s enforced client timeout with 1 retry.
  - Deterministic Offline Fallback: High-fidelity telemetry engine with realistic frame analysis for zero-latency presentation in offline/sandbox environments.

---

## 3. Directory Layout & Organization

```
amazon_developer_hackathon_aurastream/
├── INVARIANTS.md                 # Strict hackathon rules & compliance checklist
├── ARCHITECTURE.md               # This architectural specification
├── DEMO.md                       # Official 2:40 demo script & keybindings guide
├── FRICTION_LOG.md               # Empirical developer experience log (+10% bonus)
├── LICENSE                       # MIT Open Source License
├── README.md                     # Documentation, quickstart & judging guide
├── pyproject.toml                # Editable Python package registration (CLI: aurastream)
├── run.py                        # Standalone runner with dynamic sys.path resolution
├── Dockerfile                    # Containerized one-command judge deployment
├── .github/workflows/ci.yml      # CI: pytest matrix (3.11/3.13) + Docker build
├── core/                         # Tier 2: Backend MCP Server & AWS Integration
│   └── app/
│       ├── __init__.py
│       ├── main.py               # FastAPI server entry point & static mount
│       ├── commands.py           # Fire TV command bus (Alexa+ -> TV over SSE)
│       ├── aws/                  # AWS Bedrock & Telemetry engine
│       │   ├── __init__.py
│       │   ├── bedrock.py        # Converse API, Intent Router, & Circuit Breaker
│       │   └── telemetry.py      # Time-coded scene telemetry provider
│       ├── data/
│       │   └── scenes.json       # Canonical single source of truth for all 4 streams
│       ├── mcp/                  # MCP Streamable HTTP transport implementation
│       │   ├── __init__.py
│       │   └── server.py         # Spec 2025-11-25+ Streamable HTTP MCP server
│       └── models/               # Pydantic data schemas
│           ├── __init__.py
│           └── schemas.py
│   └── tests/                    # Automated pytest test suite (67/67 tests passing)
│       ├── __init__.py
│       ├── test_api_endpoints.py
│       ├── test_bedrock.py
│       ├── test_command_bus.py   # Command bus, REST dispatch & SSE generator tests
│       ├── test_intent_router.py
│       ├── test_mcp_tools.py
│       ├── test_models.py
│       ├── test_telemetry.py
│       ├── test_viewport_regression.py
│       └── capture_previews.py   # High-resolution headless Chrome preview generator
└── client/                       # Tier 1: Fire TV / Vega Client Application
    ├── index.html                # 100% full-bleed cinema stage, X-Ray drawer, Alexa bar
    ├── css/
    │   └── style.css             # Amazon Ember, frosted glass, cyan glow, auto-hide
    ├── js/
    │   ├── app.js                # Core controller, auto-hide engine, subtitle sync
    │   ├── auraOverlay.js        # X-Ray drawer tabs & Alexa light-bar orchestration
    │   ├── mcpClient.js          # Client-side MCP JSON-RPC protocol bridge
    │   ├── spatialNav.js         # 3-tier focus state machine & TV remote keycodes
    │   ├── streamData.js         # Synchronized client catalog & subtitle database
    │   └── videoPlayer.js        # 60fps video player with custom transport controls
    └── assets/                   # Video thumbnails, posters, vector badges
```
