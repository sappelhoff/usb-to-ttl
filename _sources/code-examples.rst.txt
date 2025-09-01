:orphan:

.. _code-examples:

Code examples
=============

For using these code snippets, you will have to have your hardware (e.g., based on the Arduino Leonardo) connected to a USB port of your computer.
Next, you will have to find out the port that your computer assigned to the USB device.
This requires a different procedure, depending on the operating system.

- Windows: Open the "Device Manager" and look at the Ports list (COM & LPT). The ports usually have names like ``"COM*"``.
- Linux and OSX: Check the devices in ``/dev/`` through ``ls /dev/*``. The port names differ between Linux and OSX:

  - Linux: usually ``/dev/ttyUSB*`` or ``/dev/ttyACM*``

  - OSX: usually ``/dev/tty.usbmodem*`` or ``/dev/tty.usbserial*``

The Python section below shows a way how to find the ports using the ``pyserial`` library.

Python
------

You will need to install the `pyserial`_ package via ``pip install pyserial``.

Find the port
^^^^^^^^^^^^^

We can use ``pyserial`` to find the port of our USB device

.. code-block:: python

   import serial  # imports pyserial
   import serial.tools.list_ports as list_ports

   # List all comports
   all_ports = list_ports.comports()
   print(all_ports)

   # Each entry in the `all_ports` list is a serial device. Check it's
   # description and device attributes to learn more
   first_serial_device = all_ports[0]
   print(first_serial_device.device)  # the `port_name`
   print(first_serial_device.description)  # perhaps helpful to know if this is your device

   # continue until you found your device, then note down the `port_name`

Send information
^^^^^^^^^^^^^^^^

Now open up a serial connection and send some information.

.. code-block:: python

   import serial

   port_name = "COM4"  # the name / address we found for our device

   ser = serial.Serial(
       port=port_name,
       baudrate=115200,
       bytesize=serial.EIGHTBITS,  # set this to the amount of data you want to send
       )

   # the information we want to send: 8 bits = 1 byte
   byte_to_send = bytes([1])  # send a "1"
   ser.write(byte_to_send)

   # After measurements are done, close the connection
   ser.close()

Consider sampling rate of recording device
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For event marking, we usually want to start with a state of ``0``, then set the data to some byte (e.g., ``1``), and finally reset the state to ``0`` again.
Notably, the time that the data is set to a byte different from ``0`` needs to be long enough for our recording device to notice.
How long it "long enough" depends on the sampling rate: At a sampling rate of 1000Hz, the data needs to be "switched on" for *at least* 1ms (at a sampling rate of 250Hz, for 4ms, etc.).

When using the firmware we recommend in this project for running your ``usb-to-ttl`` device, all of this is taken care of in the microcontroller, see :ref:`firmware`:

.. literalinclude:: ../scripts/commented_firmware.ino
   :language: C
   :lines: 19-27

This part of the firmware sets the data, then delays by a bit, and then resets to ``0``.
Of course, handling this issue in the microcontroller also limits the frequency with which you can send signals (every 2000 milliseconds in our firmware example), so don't forget to adjust the ``delay`` to your needs.


.. _pyserial: https://github.com/pyserial/pyserial
