/*
Device firmware for an USB trigger box (Appelhoff & Stenner, 2021).
MIT License
Copyright (c) 2021 Tristan Stenner
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

// Teensys can send emulated key presses to the host computer.
// Enabling this option "presses" the Enter key every 90ms when pin 10 is
// connected to ground. Enabled by default on Teensys when compiling with
// keyboard support unless ENABLE_KEYBOARD=0 is defined
#ifndef ENABLE_KEYBOARD
#if defined(CORE_TEENSY_KEYBOARD) || defined(USB_SERIAL_HID)
#define ENABLE_KEYBOARD 1
#else
#define ENABLE_KEYBOARD 0
#endif
#endif

// send special pin patterns to troubleshoot connection issues after receiving
// either 254 or 255 as value
#define ENABLE_PIN_TESTS 0

// function prototype; sets output pins in a loop
void setOutputsLoop(uint8_t outChar);

// device specific values for outputPins and setOutputs;
#if defined(ARDUINO_AVR_MICRO)
constexpr int outputPins[] = {2,3,4,5,6,7,8,9};
auto setOutputs = setOutputsLoop;

#elif defined(ARDUINO_AVR_LEONARDO) || defined(ARDUINO_AVR_UNO)
constexpr int outputPins[] = {0,1,2,3,4,5,6,7};
auto setOutputs = setOutputsLoop;

#elif defined(CORE_TEENSY)
constexpr int outputPins[] = {0,1,2,3,4,5,6,7};

void setOutputs(uint8_t outChar) {
  for(int i=0; i<8; ++i) digitalWriteFast(i, outChar&(1<<i));
}

#else
#warning "Unknown board"
// Fall back to default values
constexpr int outputPins[] = {0,1,2,3,4,5,6,7};
auto setOutputs = setOutputsLoop;
#endif

void setOutputsLoop(uint8_t outChar)
{
  for(int i=0;i<8;i++) digitalWrite(outputPins[i], outChar&(1<<i));
}

void clearOutputs() {
  setOutputs(0);
}

void setup() {
  Serial.begin(115200);
  for(auto pin: outputPins) pinMode(pin, OUTPUT);

  // Connect pin 10 to GND to enable keyboard emulation
  pinMode(10, INPUT_PULLUP);
}

void loop() {
#if ENABLE_KEYBOARD
	// Helper variable to keep the time of the last synthetic keyboard event
	static elapsedMillis lastKbdEvent = 0;

  if(!digitalRead(10) && lastKbdEvent >= 90) {
    digitalWriteFast(outputPins[1], HIGH);
    Keyboard.press(KEY_ENTER);
    delay(1);
    Keyboard.release(KEY_ENTER);
    digitalWriteFast(outputPins[1], LOW);
    lastKbdEvent = 0;
  }
#warning "Enabling keyboard"
#else
#warning "Keyboard disabled"
#endif

  if(!Serial.available()) return;
  // read in a single value
  uint8_t inChar = Serial.read();

  if(ENABLE_PIN_TESTS && inChar==255)
    for(inChar=1; inChar<255; inChar++){
      setOutputs(inChar);
      delay(100);
      clearOutputs();
      delay(100);
      Serial.println(inChar);
  }
  else if(ENABLE_PIN_TESTS && inChar==254)
    for(int inChar=1;inChar<256;inChar = inChar << 1){
      setOutputs(inChar);
      delay(100);
      clearOutputs();
      delay(100);
    }
  else {
    setOutputs(inChar);
    // also blink LED for visual feedback
    digitalWrite(13, HIGH);
    delay(5);
    clearOutputs();
    digitalWrite(13, LOW);
  }

  // Optional: write back the received value
  // Serial.println((int) inChar);
#if defined(CORE_TEENSY)
  // Serial.send_now();
#endif
}
