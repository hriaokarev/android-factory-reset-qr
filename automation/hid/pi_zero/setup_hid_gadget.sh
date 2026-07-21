#!/usr/bin/env bash
# Configure Raspberry Pi Zero as USB HID mouse gadget (persistent).
set -euo pipefail

CONFIG=""
for c in /boot/firmware/config.txt /boot/config.txt; do
  if [[ -f "$c" ]]; then CONFIG="$c"; break; fi
done
CMDLINE=""
for c in /boot/firmware/cmdline.txt /boot/cmdline.txt; do
  if [[ -f "$c" ]]; then CMDLINE="$c"; break; fi
done

if [[ -z "$CONFIG" || -z "$CMDLINE" ]]; then
  echo "boot config not found — run on Raspberry Pi OS"
  exit 1
fi

if ! grep -q 'dtoverlay=dwc2' "$CONFIG"; then
  echo 'dtoverlay=dwc2' | tee -a "$CONFIG"
fi
if ! grep -q 'modules-load=dwc2' "$CMDLINE"; then
  # append to first line
  sed -i 's/$/ modules-load=dwc2/' "$CMDLINE"
fi

install -d /usr/local/sbin
cat > /usr/local/sbin/adbdpc-hid-gadget.sh << 'EOF'
#!/bin/bash
set -e
modprobe dwc2 || true
modprobe libcomposite

GADGET=/sys/kernel/config/usb_gadget/adbdpc_mouse
if [[ -d "$GADGET" ]]; then
  exit 0
fi

mkdir -p "$GADGET"
cd "$GADGET"
echo 0x1d6b > idVendor
echo 0x0104 > idProduct
echo 0x0100 > bcdDevice
echo 0x0200 > bcdUSB

mkdir -p strings/0x409
echo "fedcba9876543210" > strings/0x409/serialnumber
echo "ADBPC" > strings/0x409/manufacturer
echo "FactoryReset HID Mouse" > strings/0x409/product

mkdir -p configs/c.1/strings/0x409
echo "Config 1: HID" > configs/c.1/strings/0x409/configuration
echo 250 > configs/c.1/MaxPower

mkdir -p functions/hid.usb0
echo 1 > functions/hid.usb0/protocol
echo 1 > functions/hid.usb0/subclass
echo 3 > functions/hid.usb0/report_length
# Boot mouse report descriptor
printf '\x05\x01\x09\x02\xa1\x01\x09\x01\xa1\x00\x05\x09\x19\x01\x29\x03\x15\x00\x25\x01\x95\x03\x75\x01\x81\x02\x95\x01\x75\x05\x81\x03\x05\x01\x09\x30\x09\x31\x15\x81\x25\x7f\x75\x08\x95\x02\x81\x06\xc0\xc0' > functions/hid.usb0/report_desc

ln -s functions/hid.usb0 configs/c.1/
ls /sys/class/udc > UDC
EOF
chmod +x /usr/local/sbin/adbdpc-hid-gadget.sh

cat > /etc/systemd/system/adbdpc-hid-gadget.service << 'EOF'
[Unit]
Description=ADBPC USB HID mouse gadget
After=sys-kernel-config.mount
Requires=sys-kernel-config.mount

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/adbdpc-hid-gadget.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable adbdpc-hid-gadget.service

echo "HID gadget installed. Reboot, then connect OTG cable to the phone and run tap6.py"
