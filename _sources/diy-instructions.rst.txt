:orphan:

.. _diy-instructions:

Do-it-yourself instructions
===========================

Below we provide a shopping list, build instructions, and the firmware to build your own ``usb-to-ttl`` device.

Shopping list
-------------

The items in this shopping list provide a good start to build a ``usb-to-ttl`` device without soldering and only basic assembly.
For convenience we provide the "price in euros" and the "item number" for all items, according to an online shop (we picked "Reichelt").
To find the items, simply type in the "item number" on the Reichelt shop website.

+-------------------------------+----------------+--------------------------------+
| name                          | price in euros | item-no (https://reichelt.com) |
+===============================+================+================================+
| arduino leonardo              | 18.91          | ARDUINO LEONARDO               |
+-------------------------------+----------------+--------------------------------+
| USB A to micro-B cable        | 1.64           | AK 676-AB2                     |
+-------------------------------+----------------+--------------------------------+
| 10 pin spring-loaded terminal | 1.51           | AST 021-10                     |
+-------------------------------+----------------+--------------------------------+
| 8 pin spring-loaded terminal  | 1.26           | AST 021-08                     |
+-------------------------------+----------------+--------------------------------+
| 25-pin D-SUB female connector | 0.61           | D-SUB BU 25FB                  |
+-------------------------------+----------------+--------------------------------+
| 25 pole flat ribbon cable     | 9.07           | AWG 28-25F 3M                  |
+-------------------------------+----------------+--------------------------------+

.. figure:: ./_static/materials.jpg
   :width: 400px
   :height: 300px
   :align: center
   :alt: photograph of all items

   All items needed to assemble the ``usb-to-ttl`` device.

Build instructions
------------------

Step 1
^^^^^^

.. figure:: ./_static/db25_cables.jpg
   :width: 1200
   :height: 300
   :align: center
   :alt: photograph of attaching the db 25 connector

   Attaching the db 25 connector to the cables.

Step 2
^^^^^^

.. figure:: ./_static/parport.jpg
   :width: 1160
   :height: 656
   :align: center
   :alt: schematic of the pins in the db 25 connector

   In the db 25 connector, pins 2-9 (8 pins in total) are for data.
   Pick any pin from 18-25 for the ground.

Step 3
^^^^^^

.. figure:: ./_static/prep_wires.jpg
   :width: 1200
   :height: 600
   :align: center
   :alt: photograph of preparing the wires for the terminals

   Preparing the wires for putting them into the spring-loaded terminals.
   Pick those leading to pins 2-9 for data, and one leading to any pin
   from 18-25 for the ground.

Step 4
^^^^^^

.. figure:: ./_static/cables_arduino.jpg
   :width: 800
   :height: 600
   :align: center
   :alt: photograph of connecting wires with the terminals

   Connecting the wires with the spring-loaded terminals attached to the Arduino Leonardo.
   For simplicity, connect pins 2-9 from the db 25 connector to pins 2-9 on the Arduino.
   Connect the ground from the db 25 connector (any pin from 18-25) to the ground pin
   on the Arduino.

Step 5
^^^^^^

.. figure:: ./_static/finished_lpt.jpg
   :width: 400px
   :height: 300px
   :align: center
   :alt: photograph of the finished device

   The finished device with an attached LPT cable (parallel port).

.. _firmware:

Firmware
--------

This is the firmware that should be uploaded to the microcontroller.
For uploading the firmware to the Arduino, please consult one of the abundant
tutorials in the
`Arduino documentation <https://docs.arduino.cc/software/ide-v2/tutorials/getting-started/ide-v2-uploading-a-sketch>`_.

Take care to define the ``outputPins`` according to how you connected your wires
(if you followed the instructions above, this will already be the case).

.. literalinclude:: ../scripts/commented_firmware.ino
   :language: C
   :linenos:
