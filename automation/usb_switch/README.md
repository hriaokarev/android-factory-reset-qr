# USBデータスイッチ制御

端末USBを **ラズパイ(OTG/HID)** と **PC(ADB)** の間で切り替える。

充電専用ハブではなく、**D+/D- も切替する**スイッチが必要。

## 対応バックエンド

| backend | 説明 |
|---------|------|
| `mock` | ログだけ（開発・ドライラン） |
| `gpio` | ラズパイGPIOでリレー／スイッチ基板を制御 |
| `serial` | シリアルコマンド（例: `PI\n` / `PC\n`） |
| `http` | HTTP POST で外部コントローラへ |

## CLI

```bash
python3 switch.py pi          # 端末 → ラズパイ
python3 switch.py pc          # 端末 → PC
python3 switch.py status
python3 switch.py pi --config ../automation_config.json
```

## GPIO例

`automation_config.json`:

```json
"usb_switch": {
  "backend": "gpio",
  "gpio_pin": 17,
  "gpio_pi_level": 1,
  "gpio_pc_level": 0
}
```

HIGH=Pi側、LOW=PC側など基板に合わせて `gpio_pi_level` を調整。

## 配線イメージ

```
[端末 USB-C] --- [データ切替SW] +-- [Pi OTG / Pico HID]
                                +-- [PC ADB]
              電源は常時供給でも可（基板仕様による）
```
