"""
Capture UI State Previews for Visual Audit.
Saves temp HTML in client/ so all relative assets (css/, assets/) load properly.
"""

import os
import subprocess
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CLIENT_DIR = BASE_DIR / "client"
PREVIEWS_DIR = CLIENT_DIR / "previews"
PREVIEWS_DIR.mkdir(exist_ok=True)

INDEX_HTML = CLIENT_DIR / "index.html"
with open(INDEX_HTML, "r", encoding="utf-8") as f:
    orig_html = f.read()

# 1. Voice Remote Modal Preview
modal_html = orig_html.replace(
    'id="voice-remote-modal" class="voice-modal-backdrop" style="display: none;"',
    'id="voice-remote-modal" class="voice-modal-backdrop" style="display: flex;"',
)
modal_file = CLIENT_DIR / "temp_modal.html"
modal_file.write_text(modal_html, encoding="utf-8")

cmd1 = [
    CHROME,
    "--headless=new",
    f"--screenshot={PREVIEWS_DIR / 'modal_preview.png'}",
    "--window-size=1920,1080",
    f"file:///{modal_file.as_posix()}",
]
subprocess.run(cmd1, check=True)
modal_file.unlink(missing_ok=True)
print("Captured modal_preview.png")

# 2. X-Ray Cards Overlay Preview
sample_cards = """
<div id="card-carousel" style="display: flex; opacity: 1;">
  <div class="insight-card focused" tabindex="0">
    <div class="card-badge-row">
      <span class="card-category-badge actor-badge">ACTOR PROFILE</span>
      <span class="card-confidence-badge">99% CONFIDENCE</span>
    </div>
    <div class="card-headline">Halina Reijn as Sintel</div>
    <div class="card-title">Lead Protagonist • Dragon Trainer</div>
    <div class="card-desc">A solitary warrior whose life transforms after rescuing an injured dragon whelp named Scales. Voice portrayed by acclaimed Dutch actress Halina Reijn.</div>
    <div class="card-actions-row">
      <button class="card-action-btn primary" tabindex="0">View Filmography</button>
      <button class="card-action-btn" tabindex="0">IMDb Bio</button>
    </div>
  </div>
  <div class="insight-card" tabindex="0">
    <div class="card-badge-row">
      <span class="card-category-badge actor-badge">ACTOR PROFILE</span>
      <span class="card-confidence-badge">96% CONFIDENCE</span>
    </div>
    <div class="card-headline">Thom Hoffman as The Shaman</div>
    <div class="card-title">Hermit Guide • Mystic Oracle</div>
    <div class="card-desc">An ancient hermit living in the desert ruins who interprets the dragon runes and warns Sintel of the guardian beast on the volcano peak.</div>
    <div class="card-actions-row">
      <button class="card-action-btn primary" tabindex="0">View Filmography</button>
      <button class="card-action-btn" tabindex="0">IMDb Bio</button>
    </div>
  </div>
</div>
"""
cards_html = orig_html.replace(
    '<div id="card-carousel" style="display: none; opacity: 0;"></div>',
    sample_cards,
).replace(
    '<div id="xray-backdrop-dim" class="xray-dim-layer"></div>',
    '<div id="xray-backdrop-dim" class="xray-dim-layer active"></div>',
)
cards_file = CLIENT_DIR / "temp_cards.html"
cards_file.write_text(cards_html, encoding="utf-8")

cmd2 = [
    CHROME,
    "--headless=new",
    f"--screenshot={PREVIEWS_DIR / 'cards_preview.png'}",
    "--window-size=1920,1080",
    f"file:///{cards_file.as_posix()}",
]
subprocess.run(cmd2, check=True)
cards_file.unlink(missing_ok=True)
print("Captured cards_preview.png")

# 3. Toast Notification Preview
toast_html = orig_html.replace(
    'id="aura-toast" class="aura-toast" style="display: none;"',
    'id="aura-toast" class="aura-toast visible" style="display: flex;"',
)
toast_file = CLIENT_DIR / "temp_toast.html"
toast_file.write_text(toast_html, encoding="utf-8")

cmd3 = [
    CHROME,
    "--headless=new",
    f"--screenshot={PREVIEWS_DIR / 'toast_preview.png'}",
    "--window-size=1920,1080",
    f"file:///{toast_file.as_posix()}",
]
subprocess.run(cmd3, check=True)
toast_file.unlink(missing_ok=True)
print("Captured toast_preview.png")

# 4. Subtitle Track Preview
sub_html = orig_html.replace(
    '<div id="vtt-subtitle-display" class="vtt-subtitle-display" style="display: none;"></div>',
    '<div id="vtt-subtitle-display" class="vtt-subtitle-display" style="display: block;">[Sintel] Scales... wake up, little one. The snow is clearing over the mountain pass.</div>',
)
sub_file = CLIENT_DIR / "temp_sub.html"
sub_file.write_text(sub_html, encoding="utf-8")
cmd4 = [
    CHROME,
    "--headless=new",
    f"--screenshot={PREVIEWS_DIR / 'subtitle_preview.png'}",
    "--window-size=1920,1080",
    f"file:///{sub_file.as_posix()}",
]
subprocess.run(cmd4, check=True)
sub_file.unlink(missing_ok=True)
print("Captured subtitle_preview.png")

print("All previews captured successfully!")

