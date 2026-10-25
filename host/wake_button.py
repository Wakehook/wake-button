"""Wake button host agent.

Listens to the button over USB serial and sends a critical WakeHook alert when it's held.
The hook address comes from the WAKEHOOK_URL environment variable and never touches the device.

    export WAKEHOOK_URL='https://in.wakehook.com/v1/h/…'
    python3 wake_button.py [--port /dev/tty.usbmodem1101] [--test]
"""

import argparse
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request

import serial
from serial.tools import list_ports

BAUD = 115200
COOLDOWN_S = 120          # presses within this window are the same incident
RETRY_DELAYS_S = [2, 5, 10, 30, 60]


def log(msg: str) -> None:
    print(time.strftime("%Y-%m-%d %H:%M:%S"), msg, flush=True)


def find_port() -> str | None:
    """Picks the first port that looks like a Pico or a native-USB Arduino."""
    for p in list_ports.comports():
        name = f"{p.description} {p.manufacturer or ''}".lower()
        if p.vid in (0x2E8A, 0x2341, 0x1B4F, 0x303A) or "pico" in name or "micropython" in name:
            return p.device
    return None


def send_alert(url: str, payload: dict) -> bool:
    data = json.dumps(payload).encode()
    for delay in [0, *RETRY_DELAYS_S]:
        if delay:
            time.sleep(delay)
        req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as res:
                log(f"WakeHook accepted the alert ({res.status}): {res.read().decode()}")
                return True
        except urllib.error.HTTPError as err:
            if err.code == 429:
                time.sleep(int(err.headers.get("Retry-After", "5")))
                continue
            if 400 <= err.code < 500:
                log(f"WakeHook refused the alert ({err.code}): check WAKEHOOK_URL")
                return False
            log(f"WakeHook answered {err.code}, retrying")
        except (urllib.error.URLError, TimeoutError, OSError) as err:
            log(f"Couldn't reach WakeHook ({err}), retrying")
    return False


def build_payload(args, test: bool = False) -> dict:
    location = os.environ.get("WAKE_BUTTON_LOCATION", "")
    host = socket.gethostname()
    if test:
        return {
            "title": "Wake button test",
            "body": f"Test from the wake button agent on {host}. No action needed.",
            "severity": "info",
            "dedup_key": f"{args.key}-test",
            "tags": {"source": "wake-button", "host": host},
        }
    body = args.body or "Someone held the wake button. Call them or check in right away."
    if location:
        body += f"\nLocation: {location}"
    tags = {"source": "wake-button", "host": host}
    if location:
        tags["location"] = location
    return {"title": args.title, "body": body, "severity": "critical", "dedup_key": args.key, "tags": tags}


def run(args, url: str) -> None:
    last_sent = 0.0
    while True:
        port = args.port or find_port()
        if not port:
            log("No button found; plug it in (checking again in 5 s)")
            time.sleep(5)
            continue
        try:
            with serial.Serial(port, BAUD, timeout=1) as dev:
                log(f"Listening on {port}")
                while True:
                    line = dev.readline().decode(errors="ignore").strip()
                    if not line:
                        continue
                    if line == "WAKE-BUTTON READY":
                        log("Button ready")
                    elif line == "PRESS":
                        if time.time() - last_sent < COOLDOWN_S:
                            log("Pressed again within the cooldown; same incident, not sending")
                            dev.write(b"OK\n")
                            continue
                        log("Button held: sending a critical alert")
                        ok = send_alert(url, build_payload(args))
                        if ok:
                            last_sent = time.time()
                        dev.write(b"OK\n" if ok else b"FAIL\n")
        except serial.SerialException as err:
            log(f"Lost the button ({err}); reconnecting")
            time.sleep(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a WakeHook alert when the wake button is held.")
    parser.add_argument("--port", help="serial port; found automatically if left out")
    parser.add_argument("--title", default="Wake button pressed")
    parser.add_argument("--body")
    parser.add_argument("--key", default="wake-button", help="dedup_key; presses with the same key update one incident")
    parser.add_argument("--test", action="store_true", help="send one info-level test alert and exit")
    args = parser.parse_args()

    url = os.environ.get("WAKEHOOK_URL")
    if not url:
        sys.exit("Set WAKEHOOK_URL to your source's hook address")

    if args.test:
        sys.exit(0 if send_alert(url, build_payload(args, test=True)) else 1)
    try:
        run(args, url)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
