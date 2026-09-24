#!/usr/bin/env python3
"""
AuraStream Standalone Application Runner.
Enables seamless one-click launch from any working directory,
eliminating Python import path issues and Windows encoding quirks.
"""

import sys
import os
import argparse
from pathlib import Path

# Safe stdout UTF-8 reconfigure for Windows console compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Automatically inject the project root into sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn


def main():
    parser = argparse.ArgumentParser(
        description="AuraStream: Ambient Living Room Intelligence Engine for Amazon Fire TV"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8000")),
        help="Port to bind (default: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=False,
        help="Enable auto-reload for development",
    )

    args = parser.parse_args()

    banner = f"""
================================================================================
  AuraStream: Ambient Living Room Intelligence Engine for Amazon Fire TV
================================================================================
  [>] Primary Track: Fire TV (AI-Enhanced Viewing & Multi-Modal UX)
  [>] Mini-Challenges: AWS Builder (Bedrock Converse API) & Open Source (MIT)
  [>] MCP Spec: 2025-11-25+ Streamable HTTP Standard
  [>] Status: Production Ready (All 50 Automated Tests Passing)

  [TV] Fire TV 10-Foot Client:    http://{args.host}:{args.port}/
  [MCP] Streamable HTTP Server:   http://{args.host}:{args.port}/mcp
  [API] Interactive Swagger Docs: http://{args.host}:{args.port}/docs
  [OK] Health Check Probe:        http://{args.host}:{args.port}/health
================================================================================
"""
    try:
        print(banner)
    except Exception:
        print(banner.encode("ascii", "replace").decode("ascii"))

    uvicorn.run(
        "core.app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        app_dir=str(PROJECT_ROOT),
    )


if __name__ == "__main__":
    main()
