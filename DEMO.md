# AuraStream: Official Hackathon Video & Live Demonstration Script

> **Video Duration Requirement**: Strictly **< 3:00 minutes** (under 180 seconds).  
> **Primary Track**: Fire TV (Priority Categories: *AI-Enhanced Viewing*, *Multi-Modal UX*, *Sports & Entertainment*).  
> **Mini-Challenges**: AWS Builder (Amazon Bedrock Multi-Modal Converse API) & Open Source (MIT License).  
> **Bonus**: Verified Amazon DevRel Friction Log (`FRICTION_LOG.md` for +10% judging bonus).  

---

## 1. Demo Preconditions & Environment Setup

1. **Host Environment**:
   - Python 3.10+ (Dependencies: `fastapi`, `uvicorn`, `boto3`, `mcp`, `pydantic`, `httpx`, `sse-starlette`).
   - Browser: Google Chrome, Microsoft Edge, or Fire TV / Vega OS Simulator (1080p full-bleed).
2. **Start Backend Server**:
   ```bash
   cd amazon_developer_hackathon_aurastream
   python run.py --reload
   ```
3. **Open Client in Browser / Simulator**:
   Navigate to: `http://127.0.0.1:8000/` (Press `F11` for true 10-foot fullscreen TV experience).
4. **Keybindings Legend**:
   - <kbd>SPACE</kbd> or <kbd>UP</kbd>: Open / toggle Prime Video X-Ray bottom drawer.
   - <kbd>LEFT</kbd> / <kbd>RIGHT</kbd>: Navigate X-Ray tabs or actor/soundtrack/trivia cards.
   - <kbd>DOWN</kbd>: Step focus down from tabs to content cards.
   - <kbd>V</kbd>: Activate Alexa+ Voice Remote light-bar.
   - <kbd>C</kbd>: Toggle synchronized Closed Captions / Subtitles.
   - <kbd>BACK</kbd> / <kbd>ESC</kbd>: Dismiss drawer / hide overlays back to full-bleed video.
   - <kbd>R</kbd>: Reset playback to beginning.

---

## 2. Step-by-Step Clockwork Demo Script (2:40 Total Duration)

### 🎬 Scene 1: 100% Full-Bleed Video & Prime Video X-Ray Drawer (0:00 - 0:40)
* **Visual**: Clean, full-bleed 1080p video streaming *Sintel: The Dragon's Ascent*. After 4 seconds of inactivity, all UI chrome seamlessly fades out into pure cinema viewing.
* **Action**:
  - Press <kbd>SPACE</kbd> (or D-pad <kbd>UP</kbd>) to pause and open the **Prime Video X-Ray** bottom drawer.
  - The drawer glides up with frosted glass (`backdrop-filter: blur(24px)`), displaying real-time cast: *Sintel (Lead Protagonist, 99% Bedrock Match)* and *Scales (Dragon Whelp, 97% Match)*.
  - Press D-pad <kbd>RIGHT</kbd> to switch to the **Soundtrack** tab (*Jan Morgenstern - The Quest* with animated EQ wave bars).
  - Press D-pad <kbd>RIGHT</kbd> to inspect the **Trivia** tab (*Blender open-movie facts*).
* **Voiceover / Spoken Script**:
  > *"Welcome to AuraStream, the ambient living room co-pilot connecting Amazon Fire TV, Alexa+, and AWS Bedrock. Rather than cluttering the screen with persistent widgets, AuraStream delivers a true 10-foot cinema experience. When paused, the authentic Prime Video X-Ray drawer glides into view, pulling verified cast profiles, soundtracks, and scene trivia synchronized to the exact frame."*

---

### 🎙️ Scene 2: Alexa+ Voice Remote & Bedrock Converse Reasoning (0:40 - 1:20)
* **Visual**: Press <kbd>V</kbd> (or trigger Fire TV Voice Remote).
* **Action**:
  - The authentic **Alexa bottom LED light-strip** pulses across the lower bezel with glowing cyan rings and real-time audio visualizer waveforms.
  - The simulated query fires: *"Alexa, who is on screen right now?"* (or select **"Spoiler-free recap"**).
  - A glassmorphic Alexa response card glides down from the top right, delivering an AWS Bedrock Converse API response strictly bounded to the current timestamp with zero future plot spoilers.
  - Press <kbd>ESC</kbd> to dismiss.
* **Voiceover / Spoken Script**:
  > *"With Alexa+ Voice Remote integration, viewers never have to reach for their phones. Pressing the voice key activates the signature Alexa light-bar. Powered by Amazon Bedrock and the 2025-11-25 Model Context Protocol, AuraStream queries video telemetry to answer questions or deliver spoiler-free catch-ups bounded strictly to the elapsed video."*

---

### ⚽ Scene 3: Live Sports & Bedrock Tactical AI Breakdown (1:20 - 2:00)
* **Visual**: Switch to the live sports stream.
* **Action**:
  - Open X-Ray drawer (<kbd>UP</kbd>) and navigate to the **Catalog / More Like This** tab.
  - Select **"Champions Cup: Madrid vs Manchester"** and press <kbd>ENTER</kbd>.
  - Stream switches seamlessly to the soccer broadcast. The live telemetry updates.
  - Navigate to the **Tactical AI** tab.
  - Real-time tactical metrics appear: *4-3-3 High Press formation*, *1.84 xG Expected Goals*, *62% Possession*, and *Sprint Speed Tracking*.
* **Voiceover / Spoken Script**:
  > *"AuraStream isn't just for movies. In live sports mode, AWS Bedrock vision analyzes the pitch in real-time, extracting tactical formations, team pressing traps, expected goals (xG), and player sprint velocities directly onto the living room screen."*

---

### 💬 Scene 4: Synchronized Subtitle Engine & Auto-Hide (2:00 - 2:30)
* **Visual**: Demonstrate accessibility and ambient household awareness.
* **Action**:
  - Press <kbd>C</kbd> to toggle closed captions.
  - Synchronized dialog and sports commentary subtitles render with high-contrast legibility: *"Aura Living Room Mode: Dialogue Boost (+4.5dB) • Adaptive Subtitles ON"*.
  - Let the controller rest for 4 seconds without touching any key: watch the entire HUD and controls smoothly dissolve into 100% full-screen video with only subtitles active.
* **Voiceover / Spoken Script**:
  > *"For family viewing and noisy environments, AuraStream features a synchronized subtitle engine with ambient dialogue boosting. And the moment interaction ends, the interface disappears completely—putting the content first."*

---

### 🛠️ Scene 5: Architectural Compliance & Automated Verification (2:30 - 2:50)
* **Visual**: Quick cut to terminal showing all 51 automated tests passing and the `/mcp` Streamable HTTP endpoint.
* **Command**:
  ```bash
  python -m pytest core/tests -v
  ```
* **Voiceover / Spoken Script**:
  > *"Under the hood, AuraStream is production-engineered: 51 automated tests passing, Streamable HTTP MCP server, AWS Bedrock Converse integration, and full compliance with Fire OS and Vega OS standards. Open source under the MIT License, with an empirical Amazon DevRel friction log. This is AuraStream."*

---

## 3. Pre-Flight Recording Verification Checklist

- [ ] Browser in Fullscreen mode (`F11`) at 1920x1080 resolution.
- [ ] Backend running (`python run.py --reload`) with all 51 tests verified (`python -m pytest core/tests -q`).
- [ ] Subtitles toggle (<kbd>C</kbd>) verified operational.
- [ ] 4-second auto-hide fade verified operational.
- [ ] Alexa light-bar (<kbd>V</kbd>) and X-Ray drawer (<kbd>SPACE</kbd>) verified operational.
- [ ] Final recording strictly under **180 seconds** (3:00 minutes).
