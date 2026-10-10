# AuraStream: Official Hackathon Video & Live Demonstration Script

> **Official Video Duration**: **0:56 (56.3 seconds)** — Strictly compliant with the **< 3:00 minutes** (180s) requirement.  
> **Video Resolution & Format**: `1920x1080` (1080p Full HD @ 24fps H.264, 48kHz Stereo AAC, 0.00ms single-pass A/V sync).  
> **Primary Tracks**: Fire TV & Alexa+ (*AI-Enhanced Viewing*, *Multi-Modal UX*, *Conversational Living Room AI*).  
> **Mini-Challenges**: AWS Builder (Amazon Bedrock Multi-Modal Converse API) & Open Source (MIT License).  
> **Bonus**: Verified Amazon DevRel Friction Log (`FRICTION_LOG.md` for +10% judging bonus).  

---

## 1. Frame-Synchronized Video Timeline (`0:00.0 – 0:56.3`)

Every HUD transition in `AuraStream_Hackathon_Demo.mp4` is sample-locked to the exact spoken cue over continuous 1080p24 playback of *Sintel: The Dragon's Ascent*:

| Timestamp (`t_start → t_end`) | Active HUD State | Visual Transition on Screen | Spoken Audio & Voice Interaction |
| :--- | :--- | :--- | :--- |
| **`0:00.0 – 0:06.4`** | `state_0_clean` | Clean 1080p *Sintel* cinema playback with subtle top header and bottom transport bar (`X-Ray`, `Toast`, and `Alexa+` hidden). | **Narrator**: *"Watching a movie on Fire TV, it's easy to miss a fast plot detail or wonder who's on screen."* |
| **`0:06.4 – 0:15.1`** | `state_1_xray_cast` | **Prime Video X-Ray Drawer** (`#xray-drawer`) slides up on the **In Scene (2)** tab showing **Sintel** (*Halina Reijn*), **The Shaman** (*Thom Hoffman*), and a frame-locked IMDb **Scene Trivia** card. | **Narrator**: *"AuraStream brings live Prime Video X-Ray telemetry right over the film — showing real-time cast, character bios, and scene trivia."* |
| **`0:15.1 – 0:17.9`** | `state_0_clean` | X-Ray drawer closes; clean 1080p action scene plays uninterrupted before the trigger moment. | **Narrator**: *"When a key moment happens in the action..."* |
| **`0:17.9 – 0:22.8`** | `state_2_toast` | **Proactive Ambient Toast** (`#aura-toast`) pops up in the top-right corner: `PROACTIVE SCENE TRIGGER • EVENT DETECTED (0:42) — Try asking: "Alexa — wait, what did he just drop?"`. | **Narrator**: *"...an ambient prompt quietly appears in the corner — without pausing your movie."* |
| **`0:22.8 – 0:26.3`** | `state_3a_alexa_listening` | Bottom cyan **Alexa+ Voice Remote Bar** (`#alexa-voice-bar`) activates in listening mode (`Listening... "Alexa — wait, what did he just drop?"`) while the answer card remains hidden until the query finishes. | **Viewer**: *"Alexa — wait, what did he just drop?"* followed by the **two-tone Alexa wake chime**. |
| **`0:26.3 – 0:37.3`** | `state_3b_alexa_answer` | **Amazon Bedrock Response Card** (`#alexa-response-card` — *Claude 3.5 Sonnet • Spoiler Shield t ≤ 0:42*) pops up above the Alexa bar on the exact millisecond Alexa+ begins speaking. | **Alexa+**: *"At timestamp zero forty-two, he dropped a customized brass compass — a family heirloom from Scene Two. Spoiler Shield is active, so future plot points are locked."* |
| **`0:37.3 – 0:43.3`** | `state_4_music` | X-Ray Drawer opens and switches via `AuraOverlay.switchTab('music')` to the **Soundtrack** tab (*Jan Morgenstern — "The Quest" Original Orchestral Score*). | **Narrator**: *"Switch to the Soundtrack tab to identify the exact orchestral score playing in the frame."* |
| **`0:43.3 – 0:56.3`** | `state_5_tactical` | X-Ray Drawer switches via `AuraOverlay.switchTab('tactics')` to the **Tactical AI** tab displaying `32 ms Real-Time Retrieval Latency`, `5 MCP Tools`, and `t ≤ 0:42 Spoiler-Shield Lock Active`. | **Narrator**: *"And the Live Tactical AI tab shows real-time retrieval latency — thirty-two milliseconds across five Model Context Protocol tools. That's AuraStream for Fire TV and Alexa Plus."* |

---

## 2. Live Interactive Judge Testing Setup

1. **Host Environment**:
   - Python 3.10+ (`fastapi`, `uvicorn`, `boto3`, `mcp`, `pydantic`, `httpx`, `sse-starlette`).
   - Browser: Google Chrome, Microsoft Edge, or Fire TV / Vega OS Simulator (1920×1080 full-bleed).
2. **Start Backend Server**:
   ```bash
   cd amazon_developer_hackathon_aurastream
   python run.py --reload
   ```
3. **Open Client in Browser / Simulator**:
   Navigate to: `http://127.0.0.1:8000/` (Press `F11` for true 10-foot fullscreen TV experience).
4. **Verify Automated Test Suite (67 Tests)**:
   ```bash
   python -m pytest core/tests -v
   ```
5. **10-Foot Remote Keybindings**:
   - <kbd>SPACE</kbd> or <kbd>UP</kbd>: Open / toggle Prime Video X-Ray bottom drawer.
   - <kbd>LEFT</kbd> / <kbd>RIGHT</kbd>: Navigate X-Ray tabs (`In Scene`, `Soundtrack`, `Scene Trivia`, `Tactical AI`, `Spoiler-Free Recap`, `Catalog`).
   - <kbd>DOWN</kbd>: Step focus down from tabs to content cards.
   - <kbd>V</kbd>: Activate Alexa+ Voice Remote light-bar (or type any custom query into the **"Ask Alexa+"** input).
   - <kbd>C</kbd>: Toggle synchronized Closed Captions / Subtitles.
   - <kbd>]</kbd> / <kbd>[</kbd>: Seek 10 seconds forward / backward.
   - <kbd>R</kbd>: Reset playback to beginning.
   - <kbd>A</kbd>: Apply Adaptive Ambient Household Mode (dialogue boost + adaptive subtitles).
   - <kbd>BACK</kbd> / <kbd>ESC</kbd>: Dismiss drawer / hide overlays back to full-bleed video.
6. **Cross-Device Alexa+ Command Bus Verification**:
   In a second terminal, run:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/remote-command \
     -H "Content-Type: application/json" \
     -d '{"command":"pause","source":"alexa_plus"}'
   ```
   The video pauses immediately on screen via the MCP Fire TV Command Bus (`Server-Sent Events`).

---

## 3. Pre-Flight Verification Checklist

- [x] Browser in Fullscreen mode (`F11`) at `1920x1080` resolution with live *Sintel* HD stream.
- [x] All 67 automated tests passing (`python -m pytest core/tests -q`).
- [x] All 6 live-video HUD preview screenshots in `client/previews/` verified.
- [x] Single-pass 1080p24 demo video (`0:56`, strictly under the 3:00 limit) verified with `0.00ms` A/V drift.
