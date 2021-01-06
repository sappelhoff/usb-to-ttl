// set output pins
void setOutputsLoop(uint8_t outChar);


#if defined(ARDUINO_AVR_MICRO)
constexpr int outputPins[] = {2,3,4,5,6,7,8,9};
auto setOutputs = setOutputsLoop;
#elif defined(ARDUINO_AVR_LEONARDO)
constexpr int outputPins[] = {0,1,2,3,4,5,6,7};
auto setOutputs = setOutputsLoop;
#elif defined(CORE_TEENSY)
constexpr int outputPins[] = {0,1,2,3,4,5,6,7};
void setOutputs(uint8_t outChar) {
	for(int i=0; i<8; ++i) digitalWriteFast(outputPins[i], outChar&(1<<i));
}
elapsedMillis lastKbdEvent = 0;
#else
#error "Unknown board"
#endif

void setOutputsLoop(uint8_t outChar)
{
  for(int i=0;i<8;i++) digitalWrite(outputPins[i], outChar&(1<<i));
}

void clearOutputs() {
  for(auto pin: outputPins) digitalWrite(pin, LOW);
}

void setup() {
  Serial.begin(115200);
  for(auto pin: outputPins) pinMode(pin, OUTPUT);

  // Connect pin 10 to GND to enable keyboard emulation
  pinMode(10, INPUT_PULLUP);
}

void loop() {
#if defined(CORE_TEENSY_KEYBOARD) || defined(USB_SERIAL_HID)
  if(!digitalRead(10) && lastKbdEvent >= 100) {
    Keyboard.press(KEY_ENTER);
    digitalWriteFast(outputPins[1], HIGH);
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
  uint8_t inChar = Serial.read();
  Serial.println((int) inChar);
#if defined(CORE_TEENSY)
  Serial.send_now();
#endif
  if(inChar==255)
    for(inChar=1; inChar<255; inChar++){
      setOutputs(inChar);
      delay(100);
      clearOutputs();
      delay(100);
      Serial.println(inChar);
  }
  else if(inChar==254)
    for(int inChar=1;inChar<256;inChar = inChar << 1){
      setOutputs(inChar);
      delay(100);
      clearOutputs();
      delay(100);
    }
  else {
    setOutputs(inChar);
    digitalWrite(13, HIGH);
    delay(5);
    clearOutputs();
    digitalWrite(13, LOW);
    delay(2);
  }
}
