# Wake button firmware for Raspberry Pi Pico (MicroPython).
# Hold the button and it sends "PRESS" over USB serial. The hook address stays on the computer.

import sys
import time

import select
from machine import Pin

BUTTON = Pin(15, Pin.IN, Pin.PULL_UP)   # pressed = 0
LED = Pin(14, Pin.OUT)
HOLD_MS = 1000                          # a short bump doesn't count
LED_ON_MS = 120_000

poll = select.poll()
poll.register(sys.stdin, select.POLLIN)


def blink(times, ms=120):
    for _ in range(times):
        LED.on()
        time.sleep_ms(ms)
        LED.off()
        time.sleep_ms(ms)


def read_reply():
    if poll.poll(0):
        return sys.stdin.readline().strip()
    return None


blink(2)
print("WAKE-BUTTON READY")

pressed_at = None
sent = False
led_until = 0
failing = False

while True:
    now = time.ticks_ms()

    if BUTTON.value() == 0:
        if pressed_at is None:
            pressed_at = now
        elif not sent and time.ticks_diff(now, pressed_at) >= HOLD_MS:
            print("PRESS")
            sent = True
            LED.on()
    else:
        pressed_at = None
        sent = False

    reply = read_reply()
    if reply == "OK":
        failing = False
        led_until = time.ticks_add(now, LED_ON_MS)
        LED.on()
    elif reply == "FAIL":
        failing = True

    if failing:
        LED.value((now // 100) % 2)
    elif led_until and time.ticks_diff(led_until, now) <= 0:
        led_until = 0
        LED.off()

    time.sleep_ms(10)
