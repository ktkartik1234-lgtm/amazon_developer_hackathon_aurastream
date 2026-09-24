# AuraStream: Official Hackathon Video & Live Demonstration Script

> **Video Duration Requirement**: Strictly **< 3:00 minutes** (under 180 seconds).
> **Primary Track**: Fire TV (AI-Enhanced Viewing & Multi-Modal UX).
> **Mini-Challenges**: AWS Builder (Amazon Bedrock Multi-Modal) & Open Source (MIT License).

---

## 1. Demo Preconditions & Environment Setup

1. **Host Environment**:
   - Python 3.10+ with installed dependencies (`fastapi`, `uvicorn`, `boto3`, `mcp`, `pydantic`).
   - Browser: Google Chrome, Microsoft Edge, or Fire TV / Vega Simulator.
2. **Start Backend Server**:
   ```bash
   cd amazon_developer_hackathon_aurastream
   python run.py
   ```
   *(Or from root: `python amazon_developer_hackathon_aurastream/run.py`)*
3. **Open Client in Browser / Simulator**:
   Navigate to: `http://127.0.0.1:8000/` (or open in Fire TV web runtime).
4. **Kill-Switch / Emergency Reset**:
   - Press <kbd>R</kbd> or browser reload (`Ctrl+R`) to instantly reset state to `stream_sintel` at `0:00`.
   - Backend auto-heals: If AWS credentials are not configured, Bedrock gracefully falls back to deterministic local cache with zero latency.

---

## 2. Step-by-Step 2:40 Minute Demo Script

### Scene 1: Introduction & Living Room Ambient X-Ray (0:00 - 0:35)
* **Visual**: Full-screen 1080p video begins streaming *Sintel: The Dragon's Ascent*. The right-rail Aura X-Ray HUD dynamically updates with cast members (Halina Reijn as Sintel, Thom Hoffman as The Shaman) and the original orchestral soundtrack (*Jan Morgenstern - The Quest*).
* **Keypress**:
  - D-pad <kbd>RIGHT</kbd> on pills to highlight **"Who's on Screen?"**.
  - Press <kbd>SELECT</kbd> (Enter).
* **Result**: Video smoothly dims; central interactive X-Ray cards glide into view with verified cast profiles and Bedrock confidence scores.
* **Voiceover**: *"Welcome to AuraStream, the ambient living room co-pilot connecting Fire TV, Alexa+, and AWS Bedrock."*

---

### Scene 2: Alexa+ Voice Remote Simulation (0:35 - 1:15)
* **Visual**: Press <kbd>BACK</kbd> (Escape) to dismiss the cards.
* **Keypress**:
  - Press <kbd>V</kbd> (or simulate Fire TV Voice Remote push-to-talk).
  - Voice Remote Modal slides in with Alexa ring animation. Focus is automatically trapped.
  - Press D-pad <kbd>DOWN</kbd> to select **"Catch me up (Spoiler-Free)"**.
  - Press <kbd>SELECT</kbd>.
* **Result**: AuraStream queries the Streamable HTTP MCP server and Bedrock Converse engine, instantly delivering a spoiler-free narrative recap strictly bounded to the viewer's current timestamp (no future plot spoilers).
* **Voiceover**: *"Powered by the late-2025 Streamable HTTP Model Context Protocol, AuraStream enables Alexa+ to query video telemetry and generate instant spoiler-free plot catch-ups."*

---

### Scene 3: Live Sports & Tactical AI Breakdown (1:15 - 1:55)
* **Visual**: Press D-pad <kbd>UP</kbd> to navigate to the **"More Like This"** media shelf.
* **Keypress**:
  - Navigate D-pad <kbd>RIGHT</kbd> to **"Champions Cup: Madrid vs Manchester"**.
  - Press <kbd>SELECT</kbd>.
* **Result**: Stream instantly switches to live sports. The header and telemetry HUD update in real-time.
* **Keypress**:
  - Press D-pad <kbd>DOWN</kbd> to the action dock and select **"Tactical Breakdown"**.
  - Press <kbd>SELECT</kbd>.
* **Result**: Bedrock Vision analyzes the soccer formation, displaying real-time tactical overlays: 4-3-3 High Press, 1.84 xG, possession stats, and sprint speed tracking.

---

### Scene 4: Ambient Family Mode & Subtitle Adaptation (1:55 - 2:25)
* **Visual**: Press <kbd>BACK</kbd> to close tactical cards.
* **Keypress**:
  - Press D-pad to select **"Family Mode"**.
  - Press <kbd>SELECT</kbd>.
* **Result**: A non-blocking glassmorphic ambient toast banner appears: *"Aura Living Room Mode: Dialogue Boost (+4.5dB) • Adaptive Subtitles ON"*. Zero UI freeze, zero alert modals.
* **Voiceover**: *"AuraStream adapts to household noise and viewing context, dynamically boosting dialogue and optimizing subtitle sizing for family entertainment."*

---

### Scene 5: Architecture & Compliance Wrap-Up (2:25 - 2:40)
* **Visual**: Quick cut to terminal showing `python -m pytest core/tests -v` (24 passed) and the Streamable HTTP MCP endpoint.
* **Closing**: *"Built on Fire OS, Vega OS standards, AWS Bedrock, and open-source MCP 2025-11-25. This is AuraStream."*

---

## 3. Pre-Flight Verification Checklist Before Video Recording

- [ ] Viewport is set to clean 1920x1080 (or auto-scaled window).
- [ ] Pytest suite passes 100%: `python -m pytest core/tests -v`.
- [ ] No browser alerts or prompts occur during any interaction.
- [ ] Video audio is balanced and adheres to YouTube copyright guidelines (open-source Blender Foundation media).
- [ ] Final video length is confirmed **under 180 seconds**.
