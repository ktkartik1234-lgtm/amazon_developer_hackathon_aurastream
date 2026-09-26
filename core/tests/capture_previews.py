"""
Capture UI State Previews for Visual Audit of Cinema-Grade Interface.
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

# 1. Prime Video X-Ray Open (Cast Tab)
file_xray = CLIENT_DIR / "temp_xray.html"
file_xray.write_text(orig_html, encoding="utf-8")
cmd1 = [
    CHROME,
    "--headless=new",
    f"--screenshot={PREVIEWS_DIR / 'cinema_xray_open.png'}",
    "--window-size=1920,1080",
    f"file:///{file_xray.as_posix()}",
]
subprocess.run(cmd1, check=True)
file_xray.unlink(missing_ok=True)
print("Captured cinema_xray_open.png")

# 2. X-Ray Music Tab Open
music_html = orig_html.replace(
    'class="xray-tab active" data-tab="cast"',
    'class="xray-tab" data-tab="cast"',
).replace(
    'class="xray-tab" data-tab="music"',
    'class="xray-tab active" data-tab="music"',
).replace(
    'id="tray-cast" class="tray-pane active"',
    'id="tray-cast" class="tray-pane" style="display: none;"',
).replace(
    'id="tray-music" class="tray-pane" style="display: none;"',
    'id="tray-music" class="tray-pane active" style="display: block;"',
)
file_music = CLIENT_DIR / "temp_music.html"
file_music.write_text(music_html, encoding="utf-8")
cmd2 = [
    CHROME,
    "--headless=new",
    f"--screenshot={PREVIEWS_DIR / 'cinema_music_tab.png'}",
    "--window-size=1920,1080",
    f"file:///{file_music.as_posix()}",
]
subprocess.run(cmd2, check=True)
file_music.unlink(missing_ok=True)
print("Captured cinema_music_tab.png")

# 3. Authentic Alexa Bottom Light-Bar
alexa_html = orig_html.replace(
    'id="alexa-voice-bar" class="alexa-voice-bar" style="display: none;"',
    'id="alexa-voice-bar" class="alexa-voice-bar" style="display: flex;"',
)
file_alexa = CLIENT_DIR / "temp_alexa.html"
file_alexa.write_text(alexa_html, encoding="utf-8")
cmd3 = [
    CHROME,
    "--headless=new",
    f"--screenshot={PREVIEWS_DIR / 'cinema_alexa_bar.png'}",
    "--window-size=1920,1080",
    f"file:///{file_alexa.as_posix()}",
]
subprocess.run(cmd3, check=True)
file_alexa.unlink(missing_ok=True)
print("Captured cinema_alexa_bar.png")

# 4. Pure Cinema Video (HUD Hidden)
pure_html = orig_html.replace(
    'id="tv-header" class="tv-hud-layer visible"',
    'id="tv-header" class="tv-hud-layer hidden"',
).replace(
    'id="xray-drawer" class="tv-hud-layer visible"',
    'id="xray-drawer" class="tv-hud-layer hidden"',
).replace(
    '<div id="vtt-subtitle-display" class="vtt-subtitle-display" style="display: none;"></div>',
    '<div id="vtt-subtitle-display" class="vtt-subtitle-display" style="display: block;">[Sintel] Scales... wake up, little one. The snow is clearing over the mountain pass.</div>',
)
file_pure = CLIENT_DIR / "temp_pure.html"
file_pure.write_text(pure_html, encoding="utf-8")
cmd4 = [
    CHROME,
    "--headless=new",
    f"--screenshot={PREVIEWS_DIR / 'cinema_pure_video.png'}",
    "--window-size=1920,1080",
    f"file:///{file_pure.as_posix()}",
]
subprocess.run(cmd4, check=True)
file_pure.unlink(missing_ok=True)
print("Captured cinema_pure_video.png")

print("All cinema previews captured successfully!")
