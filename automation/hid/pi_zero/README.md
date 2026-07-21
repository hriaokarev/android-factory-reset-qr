# Raspberry Pi Zero — USBガジェットHIDマウス

Pi Zero / Zero 2 W を `g_hid`（または configfs HID）でマウス化し、6タップする。

## セットアップ（一度だけ）

```bash
sudo bash setup_hid_gadget.sh
sudo reboot
```

`/boot/config.txt`（または `/boot/firmware/config.txt`）に `dtoverlay=dwc2`、  
`/boot/cmdline.txt` に `modules-load=dwc2` が入る。

## 6タップ実行

```bash
# 端末OTGにPi ZeroのUSB OTGポートを接続してから
python3 tap6.py
python3 tap6.py --count 6 --interval 0.45
```

相対座標のみ。キャリブは `--nudge` と `--center-x` / `--center-y` で調整。

## pi_agent から呼ぶ

`pi_agent.py` の `hid.backend=local_tap6` のとき、この `tap6.py` を subprocess で実行する。
