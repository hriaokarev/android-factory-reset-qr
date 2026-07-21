# Raspberry Pi Pico — HIDマウスで6タップ

CircuitPython で Pico をUSBマウス化し、ようこそ画面を6回クリックする。

## 配線・接続

1. Pico に CircuitPython を焼く  
   https://circuitpython.org/board/raspberry_pi_pico/
2. このフォルダの `code.py` を CIRCUITPY ドライブ直下へコピー
3. Pico を **端末のOTG** に接続（PCのADB側ではない）

## 動作

- 起動数秒後、相対移動で画面中央付近へ行き 6 回左クリック
- オンボードLEDがタップごとに点滅
- もう一度走らせるには Pico のリセットボタン

## 座標調整

`code.py` 先頭の定数を変更:

```python
TAP_COUNT = 6
TAP_INTERVAL = 0.45
MOVE_TO_CENTER_STEPS = 20  # 相対移動の粗さ
```

絶対座標はUSB HIDマウスでは難しいため、**起動時に大きく左上へ寄せてから中央へ移動**する方式。  
機種ごとに `MOVE_RIGHT` / `MOVE_DOWN` を調整する。

## PCからの遠隔トリガ（任意）

Pico単体はUSBシリアルでコマンドを受けられる。`code.py` は起動時自動実行。  
オーケストレーションから使う場合は **Pi Zero + pi_agent** か、PicoをPi経由のリレーでリセットする構成を推奨。
