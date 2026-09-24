"""
Automated Viewport Regression Test for AuraStream Fire TV Client.
Validates that 1080p, developer laptop (1536x864), and 720p viewports render headlessly.
"""

import os
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
    index_html = base_dir / "client" / "index.html"
    assert index_html.exists(), "index.html not found"

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_png = os.path.join(tmp_dir, f"screen_{viewport_name}.png")
        user_data_dir = os.path.join(tmp_dir, f"prof_{viewport_name}")

        cmd = [
            browser_exe,
            "--headless=new",
            f"--user-data-dir={user_data_dir}",
            f"--screenshot={out_png}",
            f"--window-size={width},{height}",
            f"file:///{index_html.as_posix()}",
        ]

        result = subprocess.run(cmd, capture_output=True, timeout=15)
        assert result.returncode == 0, f"Headless browser failed: {result.stderr.decode()}"
        assert os.path.exists(out_png), f"Screenshot not created for {viewport_name}"
        assert os.path.getsize(out_png) > 50000, f"Screenshot file too small (blank render): {os.path.getsize(out_png)} bytes"
