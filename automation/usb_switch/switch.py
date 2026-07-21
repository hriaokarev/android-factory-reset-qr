#!/usr/bin/env python3
"""USB data switch backends: mock / gpio / serial / http."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class SwitchBackend(Protocol):
    def set_target(self, target: str) -> None: ...
    def get_target(self) -> str: ...


@dataclass
class MockSwitch:
    current: str = "pc"

    def set_target(self, target: str) -> None:
        if target not in ("pi", "pc"):
            raise ValueError(target)
        print(f"[usb_switch:mock] -> {target}", flush=True)
        self.current = target

    def get_target(self) -> str:
        return self.current


@dataclass
class GpioSwitch:
    pin: int
    pi_level: int = 1
    pc_level: int = 0
    _state: str = "pc"

    def _write(self, level: int) -> None:
        try:
            import RPi.GPIO as GPIO  # type: ignore
        except ImportError as e:
            raise RuntimeError("RPi.GPIO required for gpio backend") from e
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.HIGH if level else GPIO.LOW)

    def set_target(self, target: str) -> None:
        level = self.pi_level if target == "pi" else self.pc_level
        self._write(level)
        self._state = target
        print(f"[usb_switch:gpio] pin={self.pin} -> {target}", flush=True)

    def get_target(self) -> str:
        return self._state


@dataclass
class SerialSwitch:
    port: str
    baud: int = 9600
    _state: str = "pc"

    def set_target(self, target: str) -> None:
        try:
            import serial  # type: ignore
        except ImportError as e:
            raise RuntimeError("pyserial required for serial backend") from e
        cmd = b"PI\n" if target == "pi" else b"PC\n"
        with serial.Serial(self.port, self.baud, timeout=2) as ser:
            ser.write(cmd)
        self._state = target
        print(f"[usb_switch:serial] {self.port} -> {target}", flush=True)

    def get_target(self) -> str:
        return self._state


@dataclass
class HttpSwitch:
    url: str
    _state: str = "pc"

    def set_target(self, target: str) -> None:
        data = json.dumps({"target": target}).encode()
        req = urllib.request.Request(
            self.url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
        except urllib.error.URLError as e:
            raise RuntimeError(f"HTTP switch failed: {e}") from e
        self._state = target
        print(f"[usb_switch:http] {self.url} -> {target}", flush=True)

    def get_target(self) -> str:
        return self._state


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_switch(cfg: dict[str, Any]) -> SwitchBackend:
    section = cfg.get("usb_switch", {})
    backend = section.get("backend", "mock")
    if backend == "mock":
        return MockSwitch()
    if backend == "gpio":
        return GpioSwitch(
            pin=int(section.get("gpio_pin", 17)),
            pi_level=int(section.get("gpio_pi_level", 1)),
            pc_level=int(section.get("gpio_pc_level", 0)),
        )
    if backend == "serial":
        return SerialSwitch(
            port=section.get("serial_port", "/dev/ttyUSB0"),
            baud=int(section.get("serial_baud", 9600)),
        )
    if backend == "http":
        return HttpSwitch(url=section.get("http_url", "http://127.0.0.1:8791/switch"))
    raise ValueError(f"unknown usb_switch.backend: {backend}")


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="USB data switch control")
    parser.add_argument("action", choices=["pi", "pc", "status"])
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "automation_config.json",
    )
    args = parser.parse_args(argv)

    cfg_path = args.config if args.config.exists() else None
    if cfg_path is None:
        example = Path(__file__).resolve().parent.parent / "automation_config.example.json"
        cfg = load_config(example)
        print(f"using example config (no {args.config})", flush=True)
    else:
        cfg = load_config(cfg_path)

    sw = build_switch(cfg)
    if args.action == "status":
        print(sw.get_target())
        return 0
    sw.set_target(args.action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
