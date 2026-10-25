# Wake button

A physical panic button for your desk. Hold it for a second and WakeHook rings your on-call team's phones with a **critical** alert, through Do Not Disturb, until someone acknowledges.

Useful when something is obviously wrong and you want people awake now: the office is flooding, a customer is on the phone shouting, the server room is beeping.

```
 [ button ] --USB--> [ your computer: wake-button agent ] --HTTPS--> WakeHook --> on-call phones
```

The button is a microcontroller that sends one line over USB serial when it's held. A small agent on the computer turns that into a WakeHook alert. **The hook address lives only on the computer**, never on the device, so a lost button can't page anyone.

## What you need

| Part | Notes |
|---|---|
| Raspberry Pi Pico (or Pico W) | Any RP2040 board with USB works. An Arduino-compatible board works too, see [`firmware/arduino`](firmware/arduino) |
| A big momentary push button | A 30–60 mm arcade or mushroom button is the satisfying choice |
| An LED and a 330 Ω resistor | Optional. Many arcade buttons have one built in |
| A micro-USB or USB-C data cable | A charge-only cable won't work |
| An enclosure | A small project box, or 3D-print one |

## Wiring (Pico)

| Pico pin | Goes to |
|---|---|
| GP15 | One leg of the button |
| GND (pin 38) | Other leg of the button |
| GP14 | LED anode (long leg), through the 330 Ω resistor |
| GND | LED cathode |

The button uses the Pico's internal pull-up, so no extra resistor is needed for it.

## Set up

### 1. Flash the button

1. Install [MicroPython](https://micropython.org/download/RPI_PICO/) on the Pico: hold BOOTSEL, plug it in, drop the `.uf2` file on the drive that appears.
2. Copy [`firmware/pico/main.py`](firmware/pico/main.py) to the Pico as `main.py` (with [Thonny](https://thonny.org) or `mpremote cp firmware/pico/main.py :main.py`).
3. Unplug and plug it back in. The LED blinks twice when it's ready.

### 2. Create a WakeHook source

In the [WakeHook dashboard](https://app.wakehook.com), open **Sources**, create a source with **Generic JSON**, and copy its hook address. Route it to the escalation policy that should wake up.

### 3. Run the agent

```bash
cd host
python3 -m pip install -r requirements.txt
export WAKEHOOK_URL='https://in.wakehook.com/v1/h/…'
python3 wake_button.py            # finds the button on its own
python3 wake_button.py --test     # sends an info-level test alert, no alarm
```

To keep it running in the background, see [`service/`](service) for macOS, Linux and Windows.

## Using it

| You do | What happens |
|---|---|
| Hold the button for about 1 second | A critical alert is sent; the LED stays on |
| Tap it briefly | Nothing. A short press is ignored, so a bump won't page anyone |
| Hold it again within 2 minutes | Ignored; it's the same incident |
| LED blinks fast | The alert couldn't be sent; the agent keeps retrying |

Once the on-call person resolves the incident in the app, the button is ready again.

Every press uses the same `dedup_key`, so repeated presses update one incident instead of opening many. Change the text, severity or key with `--title`, `--body` and `--key`, or set `WAKE_BUTTON_LOCATION` to say where the button is (for example `Istanbul office, 3rd floor`).

## How the serial protocol works

The device writes plain text lines at 115200 baud:

| Line | Meaning |
|---|---|
| `WAKE-BUTTON READY` | Booted |
| `PRESS` | The button was held long enough |

The agent writes back:

| Line | Meaning |
|---|---|
| `OK` | Alert accepted; LED on solid for 2 minutes |
| `FAIL` | Couldn't send; LED blinks fast |

## License

[MIT](LICENSE). WakeHook is a product of [Raspiska](https://raspiska.co).
