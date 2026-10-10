"""
Automated Viewport Regression Test for AuraStream Fire TV Client.
Validates that 1080p, developer laptop (1536x864), and 720p viewports render headlessly.
"""

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
import pytest

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def get_browser_exe():
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    for candidate in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]:
        found = shutil.which(candidate)
        if found:
            return found
    return None


@pytest.mark.parametrize(
    "width,height,viewport_name",
    [
        (1920, 1080, "1080p_tv"),
        (1536, 864, "laptop_scaled"),
        (1280, 720, "720p_hd"),
    ],
)
def test_headless_viewport_screenshot(width, height, viewport_name):
    browser_exe = get_browser_exe()
    if not browser_exe:
        pytest.skip("Chrome / Edge browser not found on host.")

    base_dir = Path(__file__).resolve().parent.parent.parent
    client_dir = base_dir / "client"
    index_html = client_dir / "index.html"
    assert index_html.exists(), "index.html not found"

    # Strip remote <source src="https://..."> video streams so headless Chrome
    # renders the local UI immediately without blocking on external CDN video streams in CI.
    raw_html = index_html.read_text(encoding="utf-8")
    offline_html = re.sub(r'<source\s+src="https://[^"]+"[^>]*>', "", raw_html)
    base_tag = f'<base href="{client_dir.resolve().as_uri()}/">'
    offline_html = offline_html.replace("<head>", f"<head>\n  {base_tag}", 1)

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_png = os.path.join(tmp_dir, f"screen_{viewport_name}.png")
        user_data_dir = os.path.join(tmp_dir, f"prof_{viewport_name}")
        temp_html_path = Path(tmp_dir) / f"index_{viewport_name}.html"
        temp_html_path.write_text(offline_html, encoding="utf-8")

        cmd = [
            browser_exe,
            "--headless=new",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            f"--user-data-dir={user_data_dir}",
            f"--screenshot={out_png}",
            f"--window-size={width},{height}",
            temp_html_path.resolve().as_uri(),
        ]

        result = subprocess.run(cmd, capture_output=True, timeout=20)
        assert result.returncode == 0, f"Headless browser failed: {result.stderr.decode(errors='ignore')}"
        assert os.path.exists(out_png), f"Screenshot not created for {viewport_name}"
        assert os.path.getsize(out_png) > 25000, f"Screenshot file too small (blank render): {os.path.getsize(out_png)} bytes"
