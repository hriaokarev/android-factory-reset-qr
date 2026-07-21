"""CircuitPython: USB HID mouse — welcome screen 6-tap for QR provisioning."""

import time
import board
import digitalio
import usb_hid
from adafruit_hid.mouse import Mouse

# --- tune per device ---
BOOT_DELAY_SEC = 3.0
TAP_COUNT = 6
TAP_INTERVAL = 0.45
# Relative moves: go top-left, then toward center-ish
NUDGE = 40
TO_TOP_LEFT = 30
TO_CENTER_X = 12
TO_CENTER_Y = 10

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

mouse = Mouse(usb_hid.devices)


def blink(times=1):
    for _ in range(times):
        led.value = True
        time.sleep(0.05)
        led.value = False
        time.sleep(0.05)


def move_steps(dx, dy, steps):
    for _ in range(steps):
        mouse.move(x=dx, y=dy)
        time.sleep(0.02)


def tap():
    mouse.click(Mouse.LEFT_BUTTON)
    blink(1)


time.sleep(BOOT_DELAY_SEC)
blink(3)

# Park near top-left then move toward center
move_steps(-NUDGE, -NUDGE, TO_TOP_LEFT)
move_steps(NUDGE, NUDGE, max(TO_CENTER_X, TO_CENTER_Y))
# Prefer horizontal then vertical for remaining
if TO_CENTER_X > TO_CENTER_Y:
    move_steps(NUDGE, 0, TO_CENTER_X - TO_CENTER_Y)
else:
    move_steps(0, NUDGE, TO_CENTER_Y - TO_CENTER_X)

time.sleep(0.3)
for i in range(TAP_COUNT):
    tap()
    time.sleep(TAP_INTERVAL)

blink(5)

# Idle: keep USB enumerated
while True:
    time.sleep(1)
