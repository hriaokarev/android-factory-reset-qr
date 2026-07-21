#!/usr/bin/env python3
"""
Raspberry Pi agent: HTTP API for HID taps + optional local USB switch.

  GET  /health
  POST /tap6          {"count":6,"interval":0.45}
  POST /switch        {"target":"pi"|"pc"}
  GET  /switch

Run on the Pi that can reach the HID gadget and/or GPIO switch:

  python3 pi_agent.py --host 0.0.0.0 --port 8790
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
TAP6 = ROOT / "hid" / "pi_zero" / "tap6.py"
SWITCH_PY = ROOT / "usb_switch" / "switch.py"

_state_lock = threading.Lock()
_config: dict[str, Any] = {}
_last_switch = "pc"


def load_config(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    example = path.with_name("automation_config.example.json")
    return json.loads(example.read_text(encoding="utf-8"))


def run_tap6(body: dict[str, Any]) -> dict[str, Any]:
    hid = _config.get("hid", {})
    count = int(body.get("count", hid.get("tap_count", 6)))
    interval = float(body.get("interval", hid.get("tap_interval_sec", 0.45)))
    delay = float(body.get("delay", hid.get("pre_tap_delay_sec", 1.0)))
    if not TAP6.exists():
        return {"ok": False, "error": f"missing {TAP6}"}
    cmd = [
        sys.executable,
        str(TAP6),
        "--count",
        str(count),
        "--interval",
        str(interval),
        "--delay",
        str(delay),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "tap6 timeout"}
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def run_switch(target: str) -> dict[str, Any]:
    global _last_switch
    cfg = ROOT / "automation_config.json"
    if not cfg.exists():
        cfg = ROOT / "automation_config.example.json"
    cmd = [sys.executable, str(SWITCH_PY), target, "--config", str(cfg)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if proc.returncode == 0:
        with _state_lock:
            _last_switch = target
    return {
        "ok": proc.returncode == 0,
        "target": target,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("pi_agent: " + (fmt % args) + "\n")

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def _send(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            self._send(200, {"ok": True, "service": "pi_agent"})
            return
        if path == "/switch":
            with _state_lock:
                target = _last_switch
            self._send(200, {"ok": True, "target": target})
            return
        self._send(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            body = self._read_json()
        except json.JSONDecodeError:
            self._send(400, {"ok": False, "error": "invalid json"})
            return
        if path == "/tap6":
            self._send(200, run_tap6(body))
            return
        if path == "/switch":
            target = body.get("target")
            if target not in ("pi", "pc"):
                self._send(400, {"ok": False, "error": "target must be pi|pc"})
                return
            self._send(200, run_switch(target))
            return
        self._send(404, {"ok": False, "error": "not found"})


def main() -> int:
    global _config
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8790)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "automation_config.json",
    )
    args = parser.parse_args()
    _config = load_config(args.config)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"pi_agent listening on http://{args.host}:{args.port}", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
