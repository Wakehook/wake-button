# Arduino variant

For boards with native USB serial: Leonardo, Micro, Pro Micro, Nano Every, ESP32-S2/S3 and similar. Open `wake_button.ino` in the Arduino IDE, pick your board and upload.

Wiring: button between **D2** and **GND** (internal pull-up), LED on **D13** (built in on most boards).

The serial protocol is the same as the Pico firmware, so the host agent works with either.
