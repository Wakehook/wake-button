// Wake button firmware for Arduino-compatible boards with native USB
// (Leonardo, Micro, Pro Micro, Nano Every, ESP32-S2/S3...). Same protocol as the Pico version.

const int BUTTON_PIN = 2;   // to GND when pressed
const int LED_PIN = 13;
const unsigned long HOLD_MS = 1000;
const unsigned long LED_ON_MS = 120000UL;

unsigned long pressedAt = 0;
bool holding = false, sent = false, failing = false;
unsigned long ledUntil = 0;
String reply;

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(115200);
  for (int i = 0; i < 2; i++) { digitalWrite(LED_PIN, HIGH); delay(120); digitalWrite(LED_PIN, LOW); delay(120); }
  Serial.println("WAKE-BUTTON READY");
}

void loop() {
  unsigned long now = millis();

  if (digitalRead(BUTTON_PIN) == LOW) {
    if (!holding) { holding = true; pressedAt = now; }
    else if (!sent && now - pressedAt >= HOLD_MS) {
      Serial.println("PRESS");
      sent = true;
      digitalWrite(LED_PIN, HIGH);
    }
  } else {
    holding = false;
    sent = false;
  }

  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      reply.trim();
      if (reply == "OK") { failing = false; ledUntil = now + LED_ON_MS; digitalWrite(LED_PIN, HIGH); }
      else if (reply == "FAIL") { failing = true; }
      reply = "";
    } else {
      reply += c;
    }
  }

  if (failing) digitalWrite(LED_PIN, (now / 100) % 2);
  else if (ledUntil && (long)(now - ledUntil) >= 0) { ledUntil = 0; digitalWrite(LED_PIN, LOW); }

  delay(10);
}
