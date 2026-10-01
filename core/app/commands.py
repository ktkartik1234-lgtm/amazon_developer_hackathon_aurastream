"""
Fire TV Remote Command Bus for AuraStream.
Bridges Alexa+ voice intents and MCP tool invocations to the paired Fire TV client
over Server-Sent Events (GET /api/events). Commands are queued in-memory with
monotonic IDs so clients can resume from their last received event (Last-Event-ID).
"""

import threading
from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Command vocabulary the Fire TV client player understands.
COMMAND_SET = {
    "play",
    "pause",
    "toggle_playback",
    "seek_forward",
    "seek_back",
    "restart",
    "switch_stream",
    "open_xray",
    "toggle_subtitles",
    "hide_hud",
}

# Commands that require an argument (e.g. which stream to switch to).
COMMANDS_REQUIRING_ARGUMENT = {"switch_stream"}

MAX_QUEUE_DEPTH = 128


class CommandValidationError(ValueError):
    """Raised when a command or its argument is not in the Fire TV vocabulary."""


class FireTVCommandBus:
    """Thread-safe in-memory command bus with monotonic event IDs."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._queue: deque = deque(maxlen=MAX_QUEUE_DEPTH)
        self._next_id = 1

    def dispatch(
        self,
        command: str,
        argument: Optional[str] = None,
        source: str = "alexa_plus",
    ) -> Dict[str, Any]:
        """Validate and enqueue a command event. Returns the serialized event."""
        command = (command or "").strip().lower()
        if command not in COMMAND_SET:
            raise CommandValidationError(
                f"Unknown command '{command}'. Supported: {', '.join(sorted(COMMAND_SET))}"
            )
        argument = (argument or "").strip() or None
        if command in COMMANDS_REQUIRING_ARGUMENT and not argument:
            raise CommandValidationError(f"Command '{command}' requires an argument (stream_id).")

        with self._lock:
            event = {
                "event_id": self._next_id,
                "command": command,
                "argument": argument,
                "source": source,
                "issued_at": datetime.now(timezone.utc).isoformat(),
            }
            self._next_id += 1
            self._queue.append(event)
            return dict(event)

    def events_since(self, last_event_id: int = 0) -> List[Dict[str, Any]]:
        """Return all queued events with event_id greater than last_event_id."""
        with self._lock:
            return [dict(e) for e in self._queue if e["event_id"] > last_event_id]

    def latest_event_id(self) -> int:
        with self._lock:
            return self._next_id - 1

    def depth(self) -> int:
        with self._lock:
            return len(self._queue)


# Global singleton shared by REST endpoints and MCP tools
command_bus = FireTVCommandBus()
