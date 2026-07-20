#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DPC="$ROOT/dpc"
DIST="$ROOT/dist"
export ANDROID_HOME="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
export JAVA_HOME="${JAVA_HOME:-/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home}"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$PATH"

mkdir -p "$DIST"

if [[ ! -f "$DPC/gradlew" ]]; then
  echo "Gradle wrapper を用意しています..."
  cd "$DPC"
  if command -v gradle >/dev/null 2>&1; then
    gradle wrapper --gradle-version 8.9
  else
    # gradle が無い場合は wrapper を直接取得
    curl -fsSL -o /tmp/gradle-8.9-bin.zip https://services.gradle.org/distributions/gradle-8.9-bin.zip
    rm -rf /tmp/gradle-8.9
    mkdir -p /tmp/gradle-8.9
    unzip -q /tmp/gradle-8.9-bin.zip -d /tmp
    /tmp/gradle-8.9/bin/gradle wrapper --gradle-version 8.9
  fi
fi

cd "$DPC"
# AGP は Java 17〜21 想定。25 だと失敗することがあるので toolchain に任せる
./gradlew :app:assembleRelease --no-daemon

APK_SRC="$DPC/app/build/outputs/apk/release/app-release.apk"
cp "$APK_SRC" "$DIST/adbdpc.apk"
echo "APK: $DIST/adbdpc.apk"
ls -lh "$DIST/adbdpc.apk"
