#!/usr/bin/env bash
# APK をビルドして GitHub Releases に公開
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
VERSION="${1:-v1.0.0}"
REPO="${GITHUB_REPO:-hriaokarev/android-factory-reset-qr}"

cd "$ROOT"
./build_dpc.sh

APK="$ROOT/dist/adbdpc.apk"
if [[ ! -f "$APK" ]]; then
  echo "APK が見つかりません: $APK"
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "gh auth login が必要です"
  exit 1
fi

if gh release view "$VERSION" -R "$REPO" >/dev/null 2>&1; then
  echo "Release $VERSION は既に存在します。アセットを更新します..."
  gh release upload "$VERSION" "$APK" --clobber -R "$REPO"
else
  gh release create "$VERSION" "$APK" \
    -R "$REPO" \
    --title "$VERSION" \
    --notes "ADB Owner DPC for factory reset QR provisioning"
fi

echo ""
echo "APK URL:"
echo "https://github.com/$REPO/releases/download/$VERSION/adbdpc.apk"
