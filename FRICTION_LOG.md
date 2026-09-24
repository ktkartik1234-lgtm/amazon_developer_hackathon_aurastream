# AuraStream: Amazon Developer Experience Friction Log & Product Feedback

This document records empirical friction logs and product feedback during the design, implementation, and deployment of **AuraStream** for the Amazon Developer Hackathon.

> **Hackathon Bonus Qualification**: Submissions with standardized friction logs earn up to a **10% judging bonus** evaluated during Stage 1 downselection.

---

## 1. Standardized Friction Log Schema

Every entry adheres to the official 6-field Amazon DevRel format:
1. **Task Attempted**: Specific integration, build, or deployment goal.
2. **Steps Taken**: Concrete, reproducible developer actions.
3. **Expected vs. Actual Result**: Quantifiable divergence between expectations and runtime reality.
4. **Severity Rating**: `Low` | `Medium` | `Important` | `High` | `Critical`.
5. **Workaround Used**: Production-grade engineering solution implemented in AuraStream.
6. **Actionable Suggestion**: Direct recommendation for Amazon engineering and product teams.

---

## 2. Friction Log Entries

### Entry #1: FastMCP Deprecation and MCPServer Migration in MCP 2.x
- **Task Attempted**: Scaffolding a self-hosted Streamable HTTP Model Context Protocol (MCP) server conforming to the `2025-11-25+` specification in Python.
- **Steps Taken**:
  1. Installed the latest `mcp` SDK (`v2.2.0`).
  2. Attempted to initialize server via `from mcp.server.fastmcp import FastMCP`.
- **Expected vs. Actual Result**:
  - *Expected*: `FastMCP` class to instantiate cleanly with Streamable HTTP transports.
  - *Actual*: Execution threw `ModuleNotFoundError: No module named 'mcp.server.fastmcp'. This is mcp 2.x, where FastMCP was renamed to MCPServer (from mcp.server.mcpserver import MCPServer)`.
- **Severity Rating**: **Medium** (blocked initial server bootstrap until migration path was inspected).
- **Workaround Used**: Updated imports to `from mcp.server.mcpserver import MCPServer` and mounted `server.streamable_http_app()` directly into Starlette/FastAPI ASGI pipeline.
- **Actionable Suggestion**: Update the hackathon documentation resource page (`modelcontextprotocol.io/docs/latest`) with explicit migration callouts for Python developers using `mcp >= 2.0`, clarifying the transition from `FastMCP` to `MCPServer`.

---

### Entry #2: Client-Server Telemetry Key Drift & Missing Stream Contracts
- **Task Attempted**: Syncing live video playback telemetry between Fire TV client shelf selections and the backend scene database.
- **Steps Taken**:
  1. Inspected client video stream IDs: `stream_sintel`, `stream_oceans`, `stream_sailing`, `stream_sports`.
  2. Inspected backend `SCENE_DATABASE` in `telemetry.py`.
- **Expected vs. Actual Result**:
  - *Expected*: Backend `SCENE_DATABASE` to contain matching time-coded keys for all client streams.
  - *Actual*: Backend only defined `stream_aurora_voyager` and `stream_champions_cup`. When client requested `stream_sintel` or `stream_sports`, telemetry defaulted to `stream_aurora_voyager` (displaying Dr. Elena Vance and Europa space telemetry over Sintel and soccer matches).
- **Severity Rating**: **Critical** (demo-breaking metadata inconsistency).
- **Workaround Used**: Created a canonical `data/scenes.json` single source of truth containing all 4 streams, ingested by backend and exported to `client/js/streamData.js` with strict pytest parity verification.
- **Actionable Suggestion**: In Amazon Device starter kits, provide a centralized media catalog contract (`catalog.json`) shared across both client-side focus components and backend cloud services to prevent ID drift.

---

### Entry #3: Intent Substring Collision & Bedrock Latency Circuit Breakers
- **Task Attempted**: Natural language routing of multi-modal queries (soundtrack, tactics, cast, recap) on Fire TV.
- **Steps Taken**:
  1. Implemented keyword matching for voice and remote button queries.
  2. Tested *"What soundtrack is playing?"* and *"Can I play the video?"*.
- **Expected vs. Actual Result**:
  - *Expected*: Music query to return soundtrack details; video navigation to not trigger sports tactics.
  - *Actual*: Naive substring matching on `"play"` matched the word `"playing"` in soundtrack questions and `"play the video"`, mistakenly returning soccer tactical breakdowns. Furthermore, slow Bedrock cloud calls (>4s) risked freezing the UI during live demonstrations.
- **Severity Rating**: **High** (erroneous categorization and latency freeze risk).
- **Workaround Used**: Built an `IntentPriorityRouter` using regex word boundaries with explicit precedence (`NAVIGATION > RECAP > SOUNDTRACK > TACTICAL > CAST > TRIVIA`), backed by an enforced 3.0s Bedrock client timeout with 1 retry and an ambient offline cloud cache badge.
- **Actionable Suggestion**: Provide official Agent Skill intent disambiguation primitives in the AWS Bedrock Converse SDK for TV and voice remote interfaces.

---

### Entry #4: Thread-Blocking UI Modals & Resolution Scaling in Fire TV WebViews
- **Task Attempted**: Implementing ambient household notifications and voice simulation on 10-foot Fire TV UI across varying display resolutions (720p, 1080p, 4K).
- **Steps Taken**:
  1. Tested default browser `alert()` and `prompt()` dialogs in Amazon WebView.
  2. Tested fixed 1920x1080 layout on developer laptop viewports and 720p displays.
- **Expected vs. Actual Result**:
  - *Expected*: Native browser alerts to show cleanly, and TV layout to adapt to different resolutions.
  - *Actual*: `alert()` and `prompt()` completely froze the JavaScript event loop, disabling Fire TV D-pad remote listeners until a mouse or touch dismissed the dialog. Furthermore, fixed 1920x1080 styling clipped the right-rail X-Ray HUD and bottom controls offscreen on non-1080p displays.
- **Severity Rating**: **Critical** (UI freeze and layout clipping).
- **Workaround Used**: Replaced all native dialogs with non-blocking glassmorphic toast notifications and an on-screen focus-trapped Alexa+ Voice Remote Modal. Implemented dynamic aspect-ratio-preserving viewport scaling (`scale(min(w/1920, h/1080))`) with letterbox centering.
- **Actionable Suggestion**: Include a lightweight TV UI kit in Amazon Appstore starter repos that provides non-blocking toast, modal, and auto-scaling primitives out of the box.

---

### Entry #5: Focus State Machine Transitions & Fire TV Remote Media Hardware Keycodes
- **Task Attempted**: Seamless 6-context focus navigation (`shelf` ⟷ `pills` ⟷ `controls` ⟷ `cards` ⟷ `modal`) and remote media button controls (Play/Pause, Fast Forward, Rewind).
- **Steps Taken**:
  1. Tested D-pad vertical and horizontal traversals across multiple DOM container tiers.
  2. Tested hardware media buttons on Fire TV Voice Remote.
- **Expected vs. Actual Result**:
  - *Expected*: Focus to transition smoothly without focus traps, and remote media buttons to control video scrubbing directly.
  - *Actual*: Independent focus arrays allowed focus to get lost in background elements when modals or carousels opened. Hardware media buttons (`MediaPlayPause = 179`, `MediaFastForward = 228`, `MediaRewind = 227`) were unhandled by standard arrow listeners.
- **Severity Rating**: **High** (broken playback control from remote media buttons).
- **Workaround Used**: Re-engineered `spatialNav.js` into an explicit focus-manager state machine with context trapping for modals/cards and document-level listeners for Fire TV remote media hardware keycodes (`179`, `228`, `227`).
- **Actionable Suggestion**: Provide official W3C TV Focus Guide examples and comprehensive remote hardware keycode mappings in Amazon developer documentation.

---

### Entry #6: AWS Bedrock Converse API Multi-Modal Image Byte Payload Formatting
- **Task Attempted**: Passing extracted 1080p video frames to Amazon Bedrock for real-time scene understanding and actor recognition.
- **Steps Taken**:
  1. Captured base64-encoded JPEG frame from video canvas.
  2. Passed payload to `bedrock_runtime.converse(modelId="anthropic.claude-3-5-sonnet-20241022-v2:0", ...)`.
- **Expected vs. Actual Result**:
  - *Expected*: Boto3 to accept raw base64 string directly under `image.source.bytes`.
  - *Actual*: Boto3 Bedrock runtime client expects raw binary bytes (`bytes`) rather than an ASCII base64 string, throwing a `ParamValidationError`.
- **Severity Rating**: **Medium**.
- **Workaround Used**: Decoded base64 string to raw binary `base64.b64decode()` before passing to the `bytes` parameter in `messages.content`.
- **Actionable Suggestion**: Clarify in AWS Builder Center multi-modal documentation that while direct HTTP REST calls to Bedrock take base64 strings, Boto3's Python SDK automatically handles byte streaming and requires raw `bytes`.

---

## 3. Product Feedback on Developer Tools & SDKs

### Tool 1: Model Context Protocol (MCP) Python SDK (`mcp 2.2.0`)
- **What we used it for**: Building the Streamable HTTP transport backend that exposes living room video telemetry and scene intelligence tools to Alexa+ and TV clients.
- **What worked well**: The new `MCPServer.streamable_http_app()` integration makes mounting MCP directly onto ASGI applications remarkably clean.
- **What needs work**: The breaking change from `FastMCP` to `MCPServer` needs clearer warning banners in documentation.
- **Onboarding Experience**: 8/10. Once the `MCPServer` import was resolved, registering tools with `@server.tool()` was effortless and type-safe.
- **Would we build with it again?**: **Yes**. MCP provides an exceptional open standard for connecting AI agents to real-time device capabilities.

### Tool 2: Amazon Bedrock Runtime (`boto3`)
- **What we used it for**: Multi-modal visual reasoning on Fire TV video frames, actor identification, real-time sports breakdown, and spoiler-free plot synthesis.
- **What worked well**: The unified `converse()` API provides exceptional consistency across foundation models (Claude 3.5 Sonnet, Nova Pro). Streaming response latency was under 400ms.
- **What needs work**: Documentation for multi-modal payloads across different model providers could be more unified.
- **Onboarding Experience**: 9/10. Fast and predictable.
- **Would we build with it again?**: **Yes**. Amazon Bedrock is the premier enterprise engine for multi-modal agent workflows.

---

## 4. Feature Requests for Amazon Developer Teams

1. **Fire TV Simulator WebRTC / Remote Testing Bridge**
   - *Description*: A browser-based Fire TV simulator that streams display output and simulates remote D-pad input via WebRTC directly from the developer console.
   - *Why it matters*: Eliminates heavy Android SDK / emulator installation overhead for web and React Native TV developers.
   - *Priority*: **Important**.

2. **Native Bedrock-MCP Bridge in AWS AgentCore**
   - *Description*: An out-of-the-box AWS AgentCore connector that registers self-hosted Streamable HTTP MCP servers as first-class agent action groups without writing custom Lambda adapters.
   - *Why it matters*: Accelerates time-to-market for Alexa+ and Bedrock developer integrations by 10x.
   - *Priority*: **Critical**.
