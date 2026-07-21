# 工場リセット〜ADB復帰 自動化

印刷QR＋ラズパイHIDマウス＋USBスイッチで、初期化後に切れたADBをPCへ自動復帰させる。

## 全体フロー

```
PC(ADB) → wipe → USB切替(Pi) → HIDで6タップ → 固定QR読取
  → プロビ完了(USBデバッグON) → USB切替(PC) → adb wait-for-device
```

## ディレクトリ

| パス | 内容 |
|------|------|
| [validate_otg.md](validate_otg.md) | セットアップ画面でOTGマウスが効くかの確認手順 |
| [jig_qr_setup.md](jig_qr_setup.md) | 端末治具＋印刷QRの位置合わせ |
| [hid/](hid/) | Pico / Pi Zero のHID 6タップ |
| [usb_switch/](usb_switch/) | USBデータスイッチ制御 |
| [orchestrate.py](orchestrate.py) | PC側オーケストレーション |
| [pi_agent.py](pi_agent.py) | ラズパイ側HTTPエージェント |

## クイックスタート

```bash
cd automation
cp automation_config.example.json automation_config.json
# 編集: PiのIP、タップ座標、スイッチ種別など

# 1. OTG確認（実機・手動）→ validate_otg.md
# 2. 治具＋QR → jig_qr_setup.md
# 3. HIDセットアップ → hid/pico/README.md または hid/pi_zero/README.md
# 4. スイッチ → usb_switch/README.md

# ドライラン（wipeしない・スイッチはmock）
python3 orchestrate.py --dry-run

# 本番
python3 orchestrate.py
```

## 前提ハード

- 印刷した `dist/provisioning_qr.png` を端末カメラ前に固定
- USBデータ切替可能なスイッチ（充電専用不可）
- HID用: Raspberry Pi Pico（CircuitPython）または Pi Zero（USBガジェット）
- 対象端末が**ようこそ画面でOTGマウス入力を受け付ける**こと
