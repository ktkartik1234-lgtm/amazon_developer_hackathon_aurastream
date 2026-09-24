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
│  │                            HERO VIDEO VIEWPORT                              │  │
│  │   4K/1080p Streaming Playback | Scrub Bar | Subtitle Dynamic Placement      │  │
│  └──────────────────────────────────────┬──────────────────────────────────────┘  │
│                                         │                                         │
│  ┌──────────────────────────────────────┴──────────────────────────────────────┐  │
│  │                        AURA PULSE MULTI-MODAL OVERLAY                       │  │
│  │  • Spatial D-Pad Focus Manager (`SpatialNav`)                               │  │
│  │  • Contextual AI Pills ("Who is on screen?", "Explain play", "Catch up")   │  │
│  │  • Interactive Visual Glassmorphism Cards (Character Graph, Sports Stats)  │  │
│  │  • Voice / Mic Input Trigger & Audio Synthesis Feedback                     │  │
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
│  │      Endpoint: `/mcp/stream` (SSE Events) & `/mcp/message` (JSON-RPC)       │  │
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
                        Boto3 / AWS SDK   │ (Bedrock Runtime)
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                         AWS BUILDER INTELLIGENCE LAYER                            │
│                                                                                   │
│   ┌───────────────────────────────┐     ┌──────────────────────────────────────┐  │
│   │        AMAZON BEDROCK         │     │            AWS AGENTCORE             │  │
│   │  Claude 3.5 Sonnet / Nova Pro │     │    Multi-Step Tool Orchestration     │  │
│   │   Multi-Modal Vision Engine   │     │    Session Memory & State Store      │  │
│   └───────────────────────────────┘     └──────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 Tier 1: Client Application (`aurastream-client`)
- **Technology**: TV Web / React Native TV compatible, conforming to Vega OS and Fire OS TV guidelines.
- **Focus Management**: Implements strict 10-foot spatial navigation. Key events:
  - `ArrowLeft` / `ArrowRight` (Codes 37, 39): Video seek or card carousel navigation.
  - `ArrowUp` / `ArrowDown` (Codes 38, 40): Traverse between Video Controls, Context Pills, and Aura Insights.
  - `Enter` / `Select` (Code 13): Trigger tool call / open detailed card.
  - `Back` / `Escape` (Code 27): Dismiss overlay or return to full-screen video.
- **Visual Design**: Glassmorphism dark mode (`rgba(15, 23, 42, 0.85)` with backdrop blur `16px`), compliant with high-contrast TV viewing distances (10 feet / 3 meters).

### 2.2 Tier 2: Streamable HTTP MCP Server (`aurastream-core`)
- **Protocol**: Model Context Protocol (MCP) Streamable HTTP Transport (Specification Version: `2025-11-25`).
- **Endpoints**:
  - `GET /mcp/sse`: Server-Sent Events stream for real-time notifications and responses.
  - `POST /mcp/messages`: JSON-RPC 2.0 message handler for client initialization, tool execution, and ping requests.
  - `GET /health`: Health check and system readiness probe.
- **Schemas**: Strict Pydantic v2 schemas validating all inputs and outputs.

### 2.3 Tier 3: AWS Builder Services
- **Service Integration**: Amazon Bedrock Runtime (`bedrock-runtime`).
- **Models**:
  - `anthropic.claude-3-5-sonnet-20241022-v2:0` or `amazon.nova-pro-v1:0` for multi-modal vision and natural conversation.
- **Resilience Strategy**:
  - Primary path: Direct call to AWS Bedrock Runtime if credentials are authenticated.
  - Verification & Demo path: High-fidelity telemetry engine with realistic frame analysis for zero-latency presentation in offline/sandbox environments.

---

## 3. Directory Layout & Organization

```
amazon_developer_hackathon_aurastream/
├── INVARIANTS.md                 # Strict hackathon rules & compliance checklist
├── ARCHITECTURE.md               # This architectural specification
├── FRICTION_LOG.md               # Empirical developer experience log (+10% bonus)
├── LICENSE                       # MIT Open Source License
├── README.md                     # Documentation, quickstart & judging guide
├── core/                         # Tier 2: Backend MCP Server & AWS Integration
│   ├── pyproject.toml            # Python packaging and dependencies
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI server entry point
│   │   ├── mcp/                  # MCP Streamable HTTP transport implementation
│   │   │   ├── __init__.py
│   │   │   ├── protocol.py       # Spec 2025-11-25 JSON-RPC schemas
│   │   │   ├── transport.py      # SSE and HTTP POST transport
│   │   │   └── tools.py          # AuraStream tool declarations
│   │   ├── aws/                  # AWS Bedrock & AgentCore integrations
│   │   │   ├── __init__.py
│   │   │   ├── bedrock_client.py # Multi-modal frame analysis
│   │   │   └── telemetry.py      # Scene telemetry and frame index
│   │   └── models/               # Pydantic data schemas
│   │       ├── __init__.py
│   │       └── schemas.py
│   └── tests/                    # Automated test suite
│       ├── test_mcp_transport.py
│       ├── test_tools.py
│       └── test_bedrock_integration.py
└── client/                       # Tier 1: Fire TV / Vega Client Application
    ├── package.json
    ├── public/
    │   ├── index.html
    │   └── assets/               # Demo video clips, posters, icons
    ├── src/
    │   ├── index.js              # TV App entry point
    │   ├── components/           # TV UI Components
    │   │   ├── VideoPlayer.jsx   # 60fps streaming player
    │   │   ├── AuraHUD.jsx       # Floating multi-modal AI overlay
    │   │   ├── ContextPill.jsx   # Dynamic quick action pills
    │   │   └── InsightCard.jsx   # Visual glassmorphism cards
    │   └── navigation/
    │       └── spatialNav.js     # 10-foot D-pad spatial focus engine
    └── tests/                    # Client UI & spatial nav tests
```
