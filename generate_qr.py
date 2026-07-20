#!/usr/bin/env python3
"""Android Enterprise QR プロビジョニング用 QR 生成."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

try:
    import qrcode
except ImportError:
    print("qrcode がありません: pip3 install 'qrcode[pil]'", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "config.json"
DEFAULT_APK = ROOT / "dist" / "adbdpc.apk"
DEFAULT_OUT = ROOT / "dist" / "provisioning_qr.png"


def urlsafe_b64_from_hex(hex_digest: str) -> str:
    import base64

    raw = bytes.fromhex(hex_digest.replace(":", "").replace(" ", ""))
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def signature_checksum(apk: Path) -> str:
    """APK 署名証明書の SHA-256 を URL-safe Base64 で返す."""
    apksigner = None
    sdk = Path.home() / "Library" / "Android" / "sdk" / "build-tools"
    if sdk.exists():
        versions = sorted(sdk.iterdir(), reverse=True)
        for v in versions:
            candidate = v / "apksigner"
            if candidate.exists():
                apksigner = candidate
                break

    if apksigner is None:
        raise RuntimeError("apksigner が見つかりません (Android SDK build-tools)")

    out = subprocess.check_output(
        [str(apksigner), "verify", "--print-certs", str(apk)],
        text=True,
        stderr=subprocess.STDOUT,
    )
    for line in out.splitlines():
        if "SHA-256 digest:" in line:
            hex_part = line.split("SHA-256 digest:")[-1].strip()
            return urlsafe_b64_from_hex(hex_part)
    raise RuntimeError(f"署名 SHA-256 を取得できませんでした:\n{out}")


def package_checksum(apk: Path) -> str:
    digest = hashlib.sha256(apk.read_bytes()).hexdigest()
    return urlsafe_b64_from_hex(digest)


def build_payload(cfg: dict, apk: Path | None) -> dict:
    wifi = cfg["wifi"]
    dpc = cfg["dpc"]

    payload = {
        "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME": dpc["component"],
        "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION": dpc[
            "download_url"
        ],
        "android.app.extra.PROVISIONING_WIFI_SSID": wifi["ssid"],
        "android.app.extra.PROVISIONING_WIFI_PASSWORD": wifi["password"],
        "android.app.extra.PROVISIONING_WIFI_SECURITY_TYPE": wifi.get("security", "WPA"),
        "android.app.extra.PROVISIONING_LEAVE_ALL_SYSTEM_APPS_ENABLED": True,
        "android.app.extra.PROVISIONING_SKIP_ENCRYPTION": True,
        "android.app.extra.PROVISIONING_SKIP_EDUCATION_SCREENS": True,
    }

    if apk and apk.exists():
        payload[
            "android.app.extra.PROVISIONING_DEVICE_ADMIN_SIGNATURE_CHECKSUM"
        ] = signature_checksum(apk)
    elif dpc.get("signature_checksum"):
        payload[
            "android.app.extra.PROVISIONING_DEVICE_ADMIN_SIGNATURE_CHECKSUM"
        ] = dpc["signature_checksum"]
    else:
        raise RuntimeError(
            "APK がありません。先に build_dpc.sh を実行するか、"
            "config.json に signature_checksum を書いてください。"
        )

    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Android 初期化用プロビジョニング QR を生成")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--apk", type=Path, default=DEFAULT_APK)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--json-out", type=Path, default=ROOT / "dist" / "provisioning.json")
    args = parser.parse_args()

    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    payload = build_payload(cfg, args.apk if args.apk.exists() else None)
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    img = qrcode.make(text)
    img.save(args.out)

    print("QR:", args.out)
    print("JSON:", args.json_out)
    print("download:", payload["android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION"])
    print("checksum:", payload["android.app.extra.PROVISIONING_DEVICE_ADMIN_SIGNATURE_CHECKSUM"])
    print()
    print("使い方: 初期化後のようこそ画面を同じ場所で6回タップ → QR読み取り")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
