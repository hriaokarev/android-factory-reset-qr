# Android ファクトリーリセット QR プロビジョニング

初期化直後の Android 端末で、QR コード 1 枚から以下を自動設定します。

- Wi-Fi 接続
- 管理アプリ（Device Owner DPC）のインストール
- USB デバッグの有効化

リポジトリ: https://github.com/hriaokarev/android-factory-reset-qr

## 必要なもの

- macOS（Android SDK / JDK 17 推奨）— QR を作り直す場合のみ
- Python 3 — QR を作り直す場合のみ
- **端末利用時は PC 不要**（APK は GitHub Releases から取得）

## クイックスタート（QR 印刷して使う）

1. [Releases](https://github.com/hriaokarev/android-factory-reset-qr/releases) から `adbdpc.apk` が公開されていることを確認
2. ローカルで QR を生成（Wi-Fi 情報を設定）
3. QR を印刷
4. 端末を工場出荷状態に戻す → ようこそ画面を **6 回タップ** → QR 読み取り

```bash
git clone https://github.com/hriaokarev/android-factory-reset-qr.git
cd android-factory-reset-qr

cp config.json.example config.json
# config.json の Wi-Fi を編集

pip3 install -r requirements.txt
python3 generate_qr.py
# → dist/provisioning_qr.png
```

## 工場リセット〜ADB復帰の自動化

印刷QR＋ラズパイHIDマウス＋USBスイッチで、初期化後に切れたADBをPCへ戻す。

詳細は **[automation/README.md](automation/README.md)**。

```bash
cd automation
cp automation_config.example.json automation_config.json
python3 orchestrate.py --dry-run
# 実機準備後:
# python3 orchestrate.py
```

流れ: `wipe` → USBをPiへ → HIDで6タップ → 固定QR読取 → USBをPCへ → `adb wait-for-device`

## APK を更新したい場合（管理者向け）

```bash
./release_apk.sh v1.0.1   # ビルド → GitHub Releases に APK 公開
python3 generate_qr.py    # 新しい checksum で QR 再生成
```

## 端末側の手順（手動）

1. 工場出荷状態に戻す
2. 初期設定の「ようこそ」画面を **同じ場所で 6 回タップ**
3. QR コードを読み取る
4. Wi-Fi 接続 → 管理アプリ導入 → USB デバッグ ON

## Device Owner からの wipe（ADB生存中）

```bash
adb shell am broadcast -a jp.factoryreset.adbdpc.ACTION_WIPE \
  -n jp.factoryreset.adbdpc/.WipeReceiver --ez confirm true
```

## 設定ファイル

| 項目 | 説明 |
|------|------|
| `wifi.ssid` | 接続先 Wi-Fi 名 |
| `wifi.password` | Wi-Fi パスワード |
| `dpc.download_url` | APK の URL（GitHub Releases 推奨） |

APK を更新したら `release_apk.sh` 実行後、必ず QR を作り直してください（署名 checksum が変わるため）。

## Google アカウントについて

**このアプリは Google ログインを自動で行いません。**

## セキュリティ

- QR コード内に **Wi-Fi パスワードが平文** で入ります
- `config.json` / `automation/automation_config.json` は Git に含めません
- 公開リポジトリにパスワードをコミットしないでください

## ライセンス

MIT
