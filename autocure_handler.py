"""
AutoCure Error Handler — Lightweight WebSocket Logger
=====================================================

Drop-in error handler for any Python service. Captures errors via
Python's standard logging framework and sends them to the AutoCure
(Self-Healing) WebSocket server.

Design:
  - Runs in the CODE'S OWN THREAD (no background threads spawned).
  - For sync apps (Flask, Django): uses synchronous `websocket-client`.
  - For async apps (FastAPI, aiohttp): uses `websockets` in the existing loop.
  - Lazy-connects on first error, auto-reconnects on send failure.
  - Tiny footprint: one WebSocket send() per error, no polling.

Quick start (Flask / any sync app):
    import logging
    from autocure_handler import attach_autocure

    attach_autocure()                       # reads .env / env vars
    logging.error("Something broke!")       # ← captured automatically

Quick start (FastAPI / any async app):
    from autocure_handler import attach_autocure
    attach_autocure()                       # same API

Environment variables (or .env file):
    AUTOCURE_WS_URL   = ws://localhost:9292/ws/logs/<user_id>
    AUTOCURE_SERVICE   = my-service-name    (default: python-service)
"""

import json
import logging
import os
import sys
import traceback
from datetime import datetime, timezone
from typing import Optional

# ---------------------------------------------------------------------------
# Try to load .env if python-dotenv is available
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Detect which WS library is available
# ---------------------------------------------------------------------------
_SYNC_WS = False
_ASYNC_WS = False

try:
    import websocket as _sync_websocket        # websocket-client (sync)
    _SYNC_WS = True
except ImportError:
    pass

try:
    import websockets as _async_websockets     # websockets (async)
    _ASYNC_WS = True
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Sync handler — no threads, in-process send()
# ---------------------------------------------------------------------------
class _SyncWSHandler(logging.Handler):
    """Sends ERROR+ logs over a synchronous WebSocket. Zero extra threads."""

    def __init__(self, ws_url: str, service_name: str):
        super().__init__(level=logging.ERROR)
        self.ws_url = ws_url
        self.service_name = service_name
        self._ws: Optional[object] = None

    # -- connection helpers (lazy + reconnect) --
    def _ensure_connected(self) -> bool:
        if self._ws is not None:
            try:
                self._ws.ping()        # fast check
                return True
            except Exception:
                self._close()

        try:
            self._ws = _sync_websocket.create_connection(
                self.ws_url, timeout=5
            )
            return True
        except Exception as exc:
            logging.getLogger("autocure").debug(
                "AutoCure WS connect failed: %s", exc
            )
            self._ws = None
            return False

    def _close(self):
        try:
            if self._ws:
                self._ws.close()
        except Exception:
            pass
        self._ws = None

    # -- the logging hook --
    def emit(self, record: logging.LogRecord):
        try:
            if not self._ensure_connected():
                return                                      # silently skip
            payload = _build_payload(record, self.service_name)
            self._ws.send(json.dumps(payload))
        except Exception:
            self._close()                                   # next call retries


# ---------------------------------------------------------------------------
# Async handler — runs in the event loop that already exists
# ---------------------------------------------------------------------------
class _AsyncWSHandler(logging.Handler):
    """Sends ERROR+ logs over an async WebSocket. No extra threads."""

    def __init__(self, ws_url: str, service_name: str):
        super().__init__(level=logging.ERROR)
        self.ws_url = ws_url
        self.service_name = service_name
        self._ws = None
        self._connecting = False

    async def _ensure_connected(self) -> bool:
        if self._ws is not None:
            try:
                await self._ws.ping()
                return True
            except Exception:
                await self._close()

        if self._connecting:
            return False
        self._connecting = True
        try:
            self._ws = await _async_websockets.connect(self.ws_url)
            return True
        except Exception as exc:
            logging.getLogger("autocure").debug(
                "AutoCure WS connect failed: %s", exc
            )
            self._ws = None
            return False
        finally:
            self._connecting = False

    async def _close(self):
        try:
            if self._ws:
                await self._ws.close()
        except Exception:
            pass
        self._ws = None

    async def _async_emit(self, record: logging.LogRecord):
        try:
            if not await self._ensure_connected():
                return
            payload = _build_payload(record, self.service_name)
            await self._ws.send(json.dumps(payload))
        except Exception:
            await self._close()

    def emit(self, record: logging.LogRecord):
        """Schedule the async send on the running event loop, or send sync."""
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._async_emit(record))
        except RuntimeError:
            # No running loop (sync context like Flask).
            # Fall back to a quick synchronous send.
            if _SYNC_WS:
                if not hasattr(self, '_sync_fallback'):
                    self._sync_fallback = _SyncWSHandler(self.ws_url, self.service_name)
                self._sync_fallback.emit(record)


# ---------------------------------------------------------------------------
# Payload builder (shared)
# ---------------------------------------------------------------------------
def _build_payload(record: logging.LogRecord, service_name: str) -> dict:
    # Build stack trace if there is exception info
    stack_trace = None
    if record.exc_info and record.exc_info[0] is not None:
        stack_trace = "".join(traceback.format_exception(*record.exc_info))

    source_file = record.pathname or ""
    line_number = record.lineno or 0

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": record.levelname,
        "message": record.getMessage(),
        "source": service_name,
        "source_file": source_file,
        "line_number": line_number,
        "stack_trace": stack_trace,
        "metadata": {
            "logger": record.name,
            "func": record.funcName,
        },
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def attach_autocure(
    ws_url: Optional[str] = None,
    service_name: Optional[str] = None,
    logger_name: Optional[str] = None,
):
    """
    Attach the AutoCure error handler to Python's logging.

    Args:
        ws_url:       WebSocket URL.  Default: env AUTOCURE_WS_URL
        service_name: Service identifier. Default: env AUTOCURE_SERVICE
        logger_name:  Logger to attach to (None = root logger).
    """
    ws_url = ws_url or os.getenv("AUTOCURE_WS_URL", "")
    service_name = service_name or os.getenv("AUTOCURE_SERVICE", "python-service")

    if not ws_url:
        logging.getLogger("autocure").warning(
            "AUTOCURE_WS_URL not set — AutoCure handler disabled"
        )
        return None

    # Prefer async handler if the async lib is available;
    # the emit() will fall back gracefully if no event loop is running.
    if _ASYNC_WS:
        handler = _AsyncWSHandler(ws_url, service_name)
    elif _SYNC_WS:
        handler = _SyncWSHandler(ws_url, service_name)
    else:
        logging.getLogger("autocure").warning(
            "Neither 'websockets' nor 'websocket-client' installed — "
            "AutoCure handler disabled.  pip install websockets  OR  pip install websocket-client"
        )
        return None

    target = logging.getLogger(logger_name)      # None → root
    target.addHandler(handler)
    logging.getLogger("autocure").info(
        "AutoCure handler attached → %s [%s]",
        ws_url, "async" if isinstance(handler, _AsyncWSHandler) else "sync"
    )
    return handler
