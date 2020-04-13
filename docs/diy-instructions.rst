:orphan:

.. _diy-instructions:

Do-it-yourself instructions
===========================

Shopping list
-------------

.. note:: Work in progress

Build instructions
------------------

.. note:: Work in progress

Firmware
--------

.. code-block:: C

   #include "Arduino.h";
   // the following pin numbers depend on where you actually put the wires on your device
   const int outputPins[] = {2,3,4,5,6,7,8,9};

   void setup() {
     Serial.begin(115200);
     // "auto" is inferring variable type from "outputPins" array = int
     for(auto pin: outputPins) pinMode(pin, OUTPUT);
   }

   // The expected byte is an ASCII character in the range of [0, 255]
   void loop() {
     // If no new information, do nothing
     if(!Serial.available()) return;
     // Else, read a single byte and format it as ...
     // type (_t) "unsigned (u) integer (int) of 8 (8) bits" = uint8_t
     uint8_t inChar = Serial.read();

     // Set the 8 pins to correspond to the byte
     setOutputs(inChar);

     // Leave the pins ON for long enough to be detected
     // This depends on the sampling rate of the device that receives the byte
     delay(2000);

     // Then clear again and wait shortly
     clearOutputs();
     delay(8);
   }

   // Quick way of setting the 8 pins by using bitwise operators
   // for each pin check using "&", whether the byte corresponding to
   // own position is ON. We get the own position through the "<<" sliding
   // of a 1 across the 00000001 ... 00000010 ... 00000100 ... etc.
   // setting a pin to LOW if zero and else HIGH
   void setOutputs(uint8_t outChar) {
     for(int i=0;i<8;i++) digitalWrite(outputPins[i], outChar&(1<<i));
   }


   // Clearing all pins, setting their output to LOW
   void clearOutputs() {
     for(auto pin: outputPins) digitalWrite(pin, LOW);
   }
