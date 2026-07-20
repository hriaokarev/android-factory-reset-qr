#!/usr/bin/env bash
# APK を同一 Wi-Fi の端末からダウンロードできるように配信する
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DIST="$ROOT/dist"
PORT="${1:-8765}"

if [[ ! -f "$DIST/adbdpc.apk" ]]; then
  echo "先に ./build_dpc.sh を実行してください"
  exit 1
fi

IP="$(ipconfig getifaddr en0 2>/dev/null || true)"
if [[ -z "$IP" ]]; then
  IP="$(ipconfig getifaddr en1 2>/dev/null || true)"
fi
echo "配信中: http://${IP:-<このMacのIP>}:$PORT/adbdpc.apk"
echo "止める: Ctrl+C"
cd "$DIST"
exec python3 -m http.server "$PORT"
