# Android ファクトリーリセット QR プロビジョニング

初期化直後の Android 端末で、QR コード 1 枚から以下を自動設定します。

- Wi-Fi 接続
- 管理アプリ（Device Owner DPC）のインストール
- USB デバッグの有効化

## 必要なもの

- macOS（Android SDK / JDK 17 推奨）
- Python 3
- 同一 Wi-Fi 上で APK を配信できる PC

## セットアップ

```bash
git clone https://github.com/YOUR_USER/android-factory-reset-qr.git
cd android-factory-reset-qr

cp config.json.example config.json
# config.json を編集（Wi-Fi SSID/パスワード、Mac の IP）

pip3 install -r requirements.txt
./build_dpc.sh
python3 generate_qr.py
./serve_apk.sh   # 別ターミナルで APK 配信
```

生成物:

- `dist/provisioning_qr.png` … 端末で読み取る QR
- `dist/provisioning.json` … QR の中身（確認用）
- `dist/adbdpc.apk` … 管理アプリ

## 端末側の手順

1. 工場出荷状態に戻す
2. 初期設定の「ようこそ」画面を **同じ場所で 6 回タップ**
3. QR コードを読み取る
4. Wi-Fi 接続 → 管理アプリ導入 → USB デバッグ ON

## 設定ファイル

| 項目 | 説明 |
|------|------|
| `wifi.ssid` | 接続先 Wi-Fi 名 |
| `wifi.password` | Wi-Fi パスワード |
| `dpc.download_url` | APK の URL（`serve_apk.sh` 実行中の Mac IP） |

Mac の IP が変わったら `config.json` を更新して `python3 generate_qr.py` を再実行してください。

## セキュリティ

- QR コード内に **Wi-Fi パスワードが平文** で入ります
- `config.json` は Git に含めません（`.gitignore` 済み）
- 公開リポジトリにパスワードをコミットしないでください

## ライセンス

MIT
