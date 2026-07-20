#!/usr/bin/env bash
# GitHub に初回公開する（要: gh auth login 済み）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO_NAME="${1:-android-factory-reset-qr}"
VISIBILITY="${2:-public}"

cd "$ROOT"

if ! gh auth status >/dev/null 2>&1; then
  echo "先に GitHub にログインしてください:"
  echo "  gh auth login"
  exit 1
fi

USER="$(gh api user -q .login)"
echo "GitHub ユーザー: $USER"
echo "リポジトリ: $USER/$REPO_NAME ($VISIBILITY)"

if git remote get-url origin >/dev/null 2>&1; then
  echo "remote origin は既に設定済み"
else
  gh repo create "$REPO_NAME" \
    --"$VISIBILITY" \
    --source=. \
    --remote=origin \
    --description "Android factory reset QR provisioning (Wi-Fi + DPC + USB debug)"
fi

git push -u origin main

echo ""
echo "公開完了: https://github.com/$USER/$REPO_NAME"
