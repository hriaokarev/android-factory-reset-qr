#!/usr/bin/env python3
"""Send relative mouse moves + clicks via /dev/hidg0 (Pi Zero gadget)."""

from __future__ import annotations

import argparse
import struct
import time
from pathlib import Path

HIDG = Path("/dev/hidg0")


def write_report(dev, buttons: int, dx: int, dy: int) -> None:
    dx = max(-127, min(127, int(dx)))
    dy = max(-127, min(127, int(dy)))
    dev.write(struct.pack("bbb", buttons & 0x07, dx, dy))
    dev.flush()


def move(dev, dx: int, dy: int, steps: int, pause: float = 0.02) -> None:
    for _ in range(steps):
        write_report(dev, 0, dx, dy)
        time.sleep(pause)


def click(dev) -> None:
    write_report(dev, 0x01, 0, 0)
    time.sleep(0.04)
    write_report(dev, 0x00, 0, 0)


def main() -> int:
    p = argparse.ArgumentParser(description="6-tap welcome screen via HID gadget")
    p.add_argument("--device", default=str(HIDG))
    p.add_argument("--count", type=int, default=6)
    p.add_argument("--interval", type=float, default=0.45)
    p.add_argument("--nudge", type=int, default=40)
    p.add_argument("--to-corner", type=int, default=30)
    p.add_argument("--center-x", type=int, default=12)
    p.add_argument("--center-y", type=int, default=10)
    p.add_argument("--delay", type=float, default=1.0)
    args = p.parse_args()

    path = Path(args.device)
    if not path.exists():
        raise SystemExit(f"{path} not found — is the HID gadget loaded?")

    time.sleep(args.delay)
    with path.open("rb+") as dev:
        n = args.nudge
        move(dev, -n, -n, args.to_corner)
        move(dev, n, n, max(args.center_x, args.center_y))
        if args.center_x > args.center_y:
            move(dev, n, 0, args.center_x - args.center_y)
        else:
            move(dev, 0, n, args.center_y - args.center_x)
        time.sleep(0.3)
        for _ in range(args.count):
            click(dev)
            time.sleep(args.interval)
    print(f"tapped {args.count} times")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
