#!/usr/bin/env python3
"""
PC orchestrator: wipe → switch USB to Pi → HID 6-tap → wait provision → switch to PC → adb.

  python3 orchestrate.py --dry-run
  python3 orchestrate.py
  python3 orchestrate.py --skip-wipe   # already wiped; only recovery path
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SWITCH_PY = ROOT / "usb_switch" / "switch.py"
DEFAULT_CONFIG = ROOT / "automation_config.json"
EXAMPLE_CONFIG = ROOT / "automation_config.example.json"


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        print(
            f"config missing: {path} — copy from automation_config.example.json",
            file=sys.stderr,
        )
        path = EXAMPLE_CONFIG
    return json.loads(path.read_text(encoding="utf-8"))


def run(cmd: list[str], timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def adb_bin() -> str:
    return shutil.which("adb") or "adb"


def adb(*args: str, timeout: float | None = 60) -> subprocess.CompletedProcess[str]:
    return run([adb_bin(), *args], timeout=timeout)


def adb_devices() -> list[str]:
    out = adb("devices", timeout=30)
    serials: list[str] = []
    for line in out.stdout.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            serials.append(parts[0])
    return serials


def http_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    timeout: float = 30,
) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def local_switch(cfg: dict[str, Any], target: str, dry_run: bool) -> None:
    config_path = DEFAULT_CONFIG if DEFAULT_CONFIG.exists() else EXAMPLE_CONFIG
    if dry_run:
        print(f"[dry-run] usb_switch -> {target}", flush=True)
        return
    proc = run(
        [sys.executable, str(SWITCH_PY), target, "--config", str(config_path)],
        timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "switch failed")
    if proc.stdout:
        print(proc.stdout, end="", flush=True)


def pi_tap6(cfg: dict[str, Any], dry_run: bool) -> None:
    agent = cfg.get("pi_agent", {})
    base = agent.get("base_url", "http://127.0.0.1:8790").rstrip("/")
    hid = cfg.get("hid", {})
    body = {
        "count": hid.get("tap_count", 6),
        "interval": hid.get("tap_interval_sec", 0.45),
        "delay": 0.5,
    }
    if dry_run:
        print(f"[dry-run] POST {base}/tap6 {body}", flush=True)
        return
    try:
        result = http_json(
            "POST",
            f"{base}/tap6",
            body,
            timeout=float(agent.get("timeout_sec", 120)),
        )
    except urllib.error.URLError as e:
        raise RuntimeError(f"pi_agent unreachable at {base}: {e}") from e
    if not result.get("ok"):
        raise RuntimeError(f"tap6 failed: {result}")
    print("tap6 ok:", result.get("stdout", ""), flush=True)


def wipe_device(cfg: dict[str, Any], dry_run: bool) -> None:
    wipe = cfg.get("wipe", {})
    method = wipe.get("method", "dpc_broadcast")
    pkg = wipe.get("package", "jp.factoryreset.adbdpc")
    countdown = int(wipe.get("countdown_sec", 5))

    serials = adb_devices()
    if not serials and not dry_run:
        raise RuntimeError("no adb device — connect phone to PC first")
    print(f"adb devices: {serials or ['(dry-run)']}", flush=True)

    if dry_run:
        print(f"[dry-run] wipe method={method} in {countdown}s", flush=True)
        return

    print(f"wipe in {countdown}s via {method} …", flush=True)
    time.sleep(countdown)

    if method == "dpc_broadcast":
        r = adb(
            "shell",
            "am",
            "broadcast",
            "-a",
            "jp.factoryreset.adbdpc.ACTION_WIPE",
            "-n",
            f"{pkg}/.WipeReceiver",
            "--ez",
            "confirm",
            "true",
            timeout=30,
        )
        print(r.stdout, r.stderr, flush=True)
        if r.returncode != 0:
            raise RuntimeError("wipe broadcast failed")
    elif method == "dpc_activity":
        r = adb(
            "shell",
            "am",
            "start",
            "-n",
            f"{pkg}/.WipeActivity",
            "--ez",
            "confirm",
            "true",
            timeout=30,
        )
        print(r.stdout, r.stderr, flush=True)
    else:
        raise RuntimeError(f"unknown wipe.method: {method}")


def wait_adb_gone(timeout_sec: float, poll: float) -> None:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if not adb_devices():
            print("adb disconnected (expected after wipe)", flush=True)
            return
        time.sleep(poll)
    print("warning: device still listed after wipe wait", flush=True)


def probe_ready(pkg: str) -> bool:
    serials = adb_devices()
    if not serials:
        return False
    r = adb("shell", "pm", "path", pkg, timeout=20)
    if r.returncode != 0 or "package:" not in r.stdout:
        return False
    marker = adb("shell", "settings", "get", "global", "adbdpc_ready", timeout=20)
    val = (marker.stdout or "").strip()
    print(f"device={serials[0]} dpc=ok adbdpc_ready={val!r}", flush=True)
    # Accept ready marker, or package present if marker unset/null
    return val in ("1", "true", "yes") or val in ("", "null", "None")


def wait_adb_ready(cfg: dict[str, Any], timeout_sec: float, dry_run: bool) -> None:
    wait = cfg.get("wait", {})
    poll = float(wait.get("poll_interval_sec", 3))
    pkg = cfg.get("wipe", {}).get("package", "jp.factoryreset.adbdpc")
    if dry_run:
        print(f"[dry-run] wait for adb + package {pkg} (timeout {timeout_sec}s)", flush=True)
        return

    print(f"waiting for adb device (timeout {timeout_sec}s)…", flush=True)
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if probe_ready(pkg):
            adb("shell", "am", "start", "-n", f"{pkg}/.MainActivity", timeout=20)
            print("ADB recovery complete", flush=True)
            return
        time.sleep(poll)
    raise TimeoutError("timed out waiting for adb + DPC after provisioning")


def warn_prereqs(cfg: dict[str, Any]) -> None:
    otg = cfg.get("otg", {})
    jig = cfg.get("jig", {})
    if not otg.get("validated"):
        print(
            "WARNING: otg.validated is false — complete automation/validate_otg.md first",
            flush=True,
        )
    if not jig.get("qr_ready"):
        print(
            "WARNING: jig.qr_ready is false — complete automation/jig_qr_setup.md first",
            flush=True,
        )


def provision_and_recover(cfg: dict[str, Any], dry_run: bool) -> None:
    """After taps: wait for Wi-Fi provisioning, periodically probe ADB on PC side."""
    wait_cfg = cfg.get("wait", {})
    prov_timeout = float(wait_cfg.get("provision_timeout_sec", 600))
    pkg = cfg.get("wipe", {}).get("package", "jp.factoryreset.adbdpc")

    if dry_run:
        print(f"[dry-run] wait up to {prov_timeout}s then USB→PC and adb wait", flush=True)
        local_switch(cfg, "pc", True)
        wait_adb_ready(cfg, float(wait_cfg.get("adb_wait_timeout_sec", 300)), True)
        return

    slice_sec = min(60.0, max(20.0, prov_timeout / 8))
    deadline = time.time() + prov_timeout
    print(
        f"provisioning window {prov_timeout}s — probing ADB every ~{slice_sec:.0f}s",
        flush=True,
    )

    while time.time() < deadline:
        time.sleep(slice_sec)
        print("=== probe: USB → PC ===", flush=True)
        local_switch(cfg, "pc", False)
        time.sleep(4)
        if probe_ready(pkg):
            adb("shell", "am", "start", "-n", f"{pkg}/.MainActivity", timeout=20)
            print("ADB recovery complete", flush=True)
            return
        print("not ready — USB → Pi again", flush=True)
        local_switch(cfg, "pi", False)

    print("=== final: USB → PC ===", flush=True)
    local_switch(cfg, "pc", False)
    wait_adb_ready(cfg, float(wait_cfg.get("adb_wait_timeout_sec", 300)), False)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Factory reset → ADB recovery orchestrator"
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-wipe", action="store_true", help="skip wipe; recovery only")
    parser.add_argument(
        "--skip-tap", action="store_true", help="skip HID taps (manual 6-tap)"
    )
    args = parser.parse_args()

    cfg_path = args.config if args.config.exists() else EXAMPLE_CONFIG
    cfg = load_config(cfg_path)
    warn_prereqs(cfg)
    wait_cfg = cfg.get("wait", {})

    print("=== phase: ensure USB=PC ===", flush=True)
    local_switch(cfg, "pc", args.dry_run)

    if not args.skip_wipe:
        print("=== phase: wipe ===", flush=True)
        wipe_device(cfg, args.dry_run)
        if not args.dry_run:
            wait_adb_gone(
                timeout_sec=float(wait_cfg.get("after_wipe_sec", 45)),
                poll=float(wait_cfg.get("poll_interval_sec", 3)),
            )
            extra = min(15.0, float(wait_cfg.get("after_wipe_sec", 45)) / 2)
            time.sleep(extra)
    else:
        print("=== phase: wipe skipped ===", flush=True)

    print("=== phase: USB → Pi (HID) ===", flush=True)
    local_switch(cfg, "pi", args.dry_run)

    if not args.skip_tap:
        print("=== phase: HID 6-tap ===", flush=True)
        delay = float(cfg.get("hid", {}).get("pre_tap_delay_sec", 8.0))
        if args.dry_run:
            print(f"[dry-run] sleep {delay}s before tap", flush=True)
        else:
            print(f"waiting {delay}s for welcome screen…", flush=True)
            time.sleep(delay)
        pi_tap6(cfg, args.dry_run)
    else:
        print("=== phase: tap skipped — do 6-tap + QR manually ===", flush=True)

    print("=== phase: wait provisioning + recover ADB ===", flush=True)
    provision_and_recover(cfg, args.dry_run)

    print("done", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(1)
